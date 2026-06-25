import asyncio
import os, json
from agents import Runner, RunConfig, Agent
from core_agents.main_agent import triage_agent
from guardrail import ResearchCheckOutput
from agents.exceptions import InputGuardrailTripwireTriggered
from agents.result import RunResultStreaming
from agents.stream_events import RawResponsesStreamEvent, RunItemStreamEvent, AgentUpdatedStreamEvent
from openai.types.responses import ResponseTextDeltaEvent
from agents import SQLiteSession, SessionSettings

MAX_HISTORY = 10
HISTORY_FILE = "conversation_history.txt"
MEMORY_FILE = "conversation_memory.json"

async def main():

    print("Research Assistant ready. Type '/exit' or '/quit' to exit.\n")

    session = SQLiteSession("default-cli", "context.db", session_settings = SessionSettings(Limit = 10))
    conversation_history = json.load(open(MEMORY_FILE)) if os.path.exists(MEMORY_FILE) else []

    active_agent : Agent = triage_agent

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("/quit", "/exit"):
            break
        if not user_input:
            continue

        if user_input.lower() == "/reset" :
            active_agent = triage_agent
            print("Session Reset.\n")
            continue

        print("Researcher: ", end = "", flush = True) 

        try :

            result: RunResultStreaming = Runner.run_streamed(
            active_agent, 
            user_input,
            max_turns = 10,
            session = session,
            run_config = RunConfig(
                workflow_name = "Researcher Agent"
            )
            )
            SILENT_AGENTS = {"Planner_Agent", "Researcher_Agent"}
            current_agent = "Triage_Agent"

            async for event in result.stream_events():
                if isinstance(event, AgentUpdatedStreamEvent):
                    agent_name = event.new_agent.name
                    print(f"\n  [handoff → {agent_name}]", flush=True)
                    current_agent = agent_name
                    if agent_name == "Writer_Agent":
                        print()

                elif isinstance(event, RawResponsesStreamEvent):
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        chunk: str | None = getattr(event.data, "delta", None)
                        if chunk and current_agent not in SILENT_AGENTS:
                            print(chunk, end="", flush=True)

                elif isinstance(event, RunItemStreamEvent):
                    if event.name == "tool_called":
                        tool_name: str = getattr(event.item.raw_item, "name", "?")
                        print(f"\n  [calling {tool_name}]", flush=True)
                        
            
            print("\n")

            conversation_history.append({"user": user_input, "assistant": result.final_output or ""})
            conversation_history = conversation_history[-MAX_HISTORY:]

            json.dump(conversation_history, open(MEMORY_FILE, "w"))

            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                f.write(f"USER: {user_input}\n\nASSISTANT:\n{result.final_output or ''}\n\n---\n\n")
                
            active_agent = result.last_agent

        except InputGuardrailTripwireTriggered as e:
            check: ResearchCheckOutput = e.guardrail_result.output.output_info
            print(f"Sorry! i can't help with this request.\nReason : {check.reasoning}\n")

if __name__ == "__main__":
    asyncio.run(main())
