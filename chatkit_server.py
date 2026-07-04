"""
ChatKit server for the Agentic Researcher pipeline.

Bridges ChatKit's chat protocol to your existing Agents SDK pipeline
(Triage -> Planner -> Researcher -> Writer) using the official
chatkit.agents helpers.
"""

from datetime import datetime
from typing import AsyncIterator

from agents import Agent, Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from agents.result import RunResultStreaming

from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ThreadItemDoneEvent,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
)

from core_agents.main_agent import triage_agent
from core_agents.planner import planner_agent
from core_agents.researcher import researcher_agent
from core_agents.writter import writer_agent
from guardrail import ResearchCheckOutput
from chatkit_store import MemoryStore

# Maps agent names back to Agent objects so we can resume a pipeline
# mid-handoff on the next user turn (mirrors `active_agent` in main.py).
AGENTS_BY_NAME: dict[str, Agent] = {
    "Triage_Agent": triage_agent,
    "Planner_Agent": planner_agent,
    "Researcher_Agent": researcher_agent,
    "Writer_Agent": writer_agent,
}

MAX_THREAD_ITEMS = 40  # how many past items to feed back into the agent as context


class ResearchChatKitServer(ChatKitServer[dict]):
    def __init__(self):
        super().__init__(store=MemoryStore())

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:

        # Pull recent thread history and convert it to Agents SDK input items.
        items_page = await self.store.load_thread_items(
            thread.id, after=None, limit=MAX_THREAD_ITEMS, order="asc", context=context,
        )
        input_items = await simple_to_agent_input(items_page.data)

        # Resume wherever the last turn left off (e.g. mid-handoff at Researcher_Agent).
        agent_name = (thread.metadata or {}).get("active_agent", "Triage_Agent")
        active_agent = AGENTS_BY_NAME.get(agent_name, triage_agent)

        agent_context = AgentContext(thread=thread, store=self.store, request_context=context)

        try:
            result: RunResultStreaming = Runner.run_streamed(
                active_agent,
                input_items,
                max_turns=10,
                context=agent_context,
            )

            async for event in stream_agent_response(agent_context, result):
                yield event

            # Remember which agent we ended on, so the next message resumes correctly.
            thread.metadata = {**(thread.metadata or {}), "active_agent": result.last_agent.name}
            await self.store.save_thread(thread, context)

        except InputGuardrailTripwireTriggered as e:
            check: ResearchCheckOutput = e.guardrail_result.output.output_info
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    thread_id=thread.id,
                    id=self.store.generate_item_id("message", thread, context),
                    created_at=datetime.now(),
                    content=[
                        AssistantMessageContent(
                            text=f"Sorry, I can't help with this request.\nReason: {check.reasoning}"
                        )
                    ],
                ),
            )
