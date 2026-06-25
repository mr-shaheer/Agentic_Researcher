from agents import Agent
from core_agents.writter import writer_agent
from tool import web_search
from model import low_model


researcher_agent = Agent(
    name = "Researcher_Agent",
    instructions = """
    You are a research extraction agent.

    Your job is to collect and compress useful information.

    Rules:
    - Use search/web results only
    - Extract key facts only
    - Remove duplicates and irrelevant data

    Output:
    - Bullet points grouped by topic

    Note :
    - After collecting the bullet points, immediately call transfer_to_Writer_Agent.
""",
    model = low_model,
    tools = [web_search],
    handoffs = [writer_agent]
)