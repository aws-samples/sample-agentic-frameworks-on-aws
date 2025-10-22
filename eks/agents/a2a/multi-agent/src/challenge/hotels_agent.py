from strands import Agent, tool
import os
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")

@tool
def hotel_agent(query: str) -> str:
    """
    An AI Agent that provides hotel recommendations based on a US City

    Args:
        query (str): The natural language query to send to the AI Agent for hotel recommendations
    Returns:
        str: Response from the agent
    """
    agent = Agent(
        model=BEDROCK_MODEL_ID,
        system_prompt="""
        You are helpful travel assistant that provides the user with hotel recommendations
        """
    )
    return agent(query)
