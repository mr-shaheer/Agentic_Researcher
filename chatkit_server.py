from datetime import datetime
from typing import AsyncIterator

from agents import Agent, Runner, SQLiteSession, SessionSettings, RunConfig
from agents.exceptions import InputGuardrailTripwireTriggered
from agents.result import RunResultStreaming

from chatkit.agents import AgentContext, stream_agent_response
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

AGENTS_BY_NAME: dict[str, Agent] = {
    "Triage_Agent": triage_agent,
    "Planner_Agent": planner_agent,
    "Researcher_Agent": researcher_agent,
    "Writer_Agent": writer_agent,
}

SHARED_SESSION_ID = "default-cli"
SHARED_SESSION_DB = "context.db"


class ResearchChatKitServer(ChatKitServer[dict]):
    def __init__(self):
        super().__init__(store=MemoryStore())
        self.session = SQLiteSession(
            SHARED_SESSION_ID,
            SHARED_SESSION_DB,
            session_settings=SessionSettings(limit=10),
        )

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:

        agent_name = (thread.metadata or {}).get("active_agent", "Triage_Agent")
        active_agent = AGENTS_BY_NAME.get(agent_name, triage_agent)

        agent_context = AgentContext(thread=thread, store=self.store, request_context=context)

        user_text = input_user_message.content[0].text if input_user_message else ""

        try:
            result: RunResultStreaming = Runner.run_streamed(
                active_agent,
                user_text,
                max_turns=10,
                session=self.session,
                run_config = RunConfig(
                workflow_name = "Researcher Agent"
                ),
                context=agent_context,
            )

            async for event in stream_agent_response(agent_context, result):
                yield event

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