import boto3
from langchain_aws import ChatBedrock
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

class BedrockLLMClient:
    def __init__(self, region_name="us-east-1"):
        import os
        import urllib3
        
        # Disable SSL warnings for testing
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        os.environ['AWS_DEFAULT_REGION'] = region_name
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        
        self.bedrock = boto3.client(
            "bedrock-runtime", 
            region_name=region_name,
            verify=False
        )
        self.llm = ChatBedrock(
            client=self.bedrock,
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={"max_tokens": 1000, "temperature": 0.1}
        )
    
    def create_agent(self, tools: list, system_prompt: str) -> AgentExecutor:
        """Create a LangChain agent with Bedrock Claude"""
        prompt = PromptTemplate.from_template(
            f"{system_prompt}\n\n"
            "You have access to the following tools:\n{tools}\n\n"
            "Use the following format:\n"
            "Question: the input question you must answer\n"
            "Thought: you should always think about what to do\n"
            "Action: the action to take, should be one of [{tool_names}]\n"
            "Action Input: the input to the action\n"
            "Observation: the result of the action\n"
            "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
            "Thought: I now know the final answer\n"
            "Final Answer: the final answer to the original input question\n\n"
            "Question: {input}\n"
            "Thought: {agent_scratchpad}"
        )
        
        agent = create_react_agent(self.llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=3, handle_parsing_errors=True)