from strands import Agent, tool
import os
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")

@tool
def hotel_agent_as_tool(query: str) -> str:
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
