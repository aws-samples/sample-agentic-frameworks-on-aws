from strands import Agent, tool
import os
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")

@tool
def hotel_agent(query: str) -> str:
    """
    PLACEHOLDER Agent description

    Args:
        query (str): PLACEHOLDER argument description
    Returns:
        str: Response from the agent
    """
    agent = Agent(
        model=BEDROCK_MODEL_ID,
        system_prompt="""
        PLACEHOLDER of system prompt
        """
    )
    return agent(query)
