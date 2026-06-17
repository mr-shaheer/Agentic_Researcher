import asyncio
from agents import Runner, RunConfig
from core_agents.main_agent import triage_agent
from guardrail import ResearchCheckOutput
from agents.exceptions import InputGuardrailTripwireTriggered
from agents.result import RunResultStreaming
from agents.stream_events import RawResponsesStreamEvent, RunItemStreamEvent, AgentUpdatedStreamEvent
from openai.types.responses import ResponseTextDeltaEvent

async def main():

    print("Research Assistant ready. Type 'quit' to exit.\n")



    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        print("Researcher: ", end = "", flush = True) 

        try :

            result: RunResultStreaming = Runner.run_streamed(
            triage_agent, 
            user_input,
            max_turns = 10,
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


            history_file = "conversation_history.txt"
            entry = f"USER: {user_input}\n\nASSISTANT:\n{result.final_output}\n\n---\n"
            with open(history_file, "a", encoding="utf-8") as f:
                f.write(entry)

            with open(history_file, "r", encoding="utf-8") as f:
                content = f.read()
            blocks = content.split("\n---\n")
            if len(blocks) > 10:
                with open(history_file, "w", encoding="utf-8") as f:
                    f.write("\n---\n".join(blocks[-10:]))

        
        except InputGuardrailTripwireTriggered as e:
            check: ResearchCheckOutput = e.guardrail_result.output.output_info
            print(f"Sorry! i can't help with this request.\nReason : {check.reasoning}\n")

if __name__ == "__main__":
    asyncio.run(main())
