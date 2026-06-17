from agents import Agent
from core_agents.researcher import researcher_agent
from model import low_model

planner_agent = Agent(
    name = "Planner_Agent",
    instructions = """
You are a planning agent.

Your job is to convert the user request into structured research steps.

Rules:
- Break the request into 3-5 clear steps
- Keep steps simple and searchable
- Do not search the web

Output :
- Output only a numbered plan.

Note :
- After outputting the plan, immediately call transfer_to_Researcher_Agent.
""",
    model = low_model,
    handoffs = [researcher_agent]
)