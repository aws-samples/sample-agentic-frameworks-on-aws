from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
import logging
import os
import time
import streamlit as st



# Enables Strands debug log level
logging.getLogger("strands").setLevel(logging.ERROR)



model = BedrockModel(
        # **model_config
        max_tokens=8192,
        model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
        streaming=False
    )

def my_callback_handler(**kwargs) :

    if "message" in kwargs and kwargs["message"].get("role") == "assistant" :
            for content in kwargs["message"]["content"] :
                if "text" in content:
                    #print(str(kwargs))
                    st.write(f'**MBR Assistant:** {content["text"]}')
                    
                if "toolUse" in content :
                    if str(content["toolUse"]["name"]) == "read_quip" :
                        st.write(f'\n**MBR Assistant:** Reading Quip {content["toolUse"]["input"]["documentId"]}')
                    elif str(content["toolUse"]["name"]) == "wait_60" :
                        st.write("\nProcessing result...\n")
                    elif str(content["toolUse"]["name"]) == "get_arxiv_list" :
                        st.write(f'\n**Research Assistant:** Doing an ArXiv Search on {content["toolUse"]["input"]["subject"]}')
                    elif str(content["toolUse"]["name"]) == "get_stock_info" :
                        st.write(f'\n**Research Assistant:** Retieving current stock information on {content["toolUse"]["input"]["ticker"]}')
                    elif str(content["toolUse"]["name"]) == "get_company_news" :
                        st.write(f'\n**Research Assistant:** Getting current financial news and company information {content["toolUse"]["input"]["ticker"]}')
                    else:  
                        print("----------------TOOL CALL----------------------")
                        #print(str(kwargs))
                        print(str(content["toolUse"].get("name")))
                        print(str(content["toolUse"].get("input")))
                        print("------------------------------------")




# Connect to an MCP server using stdio transport
# Note: uvx command syntax differs by platform


# For macOS/Linux:
stdio_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="/Users/smithzgg/.toolbox/bin/amzn-mcp" 
    )
))
if 'file_list' not in st.session_state:
    st.session_state['file_list'] = []


st.write("MBR Generation Tool")

work_pane=st.empty()
prompt = None

if prompt is None:
    with work_pane.container():       
        template_file = st.text_input("Enter the source format file or DEFAULT to use the standard MBR Format")
        st.write(f'Template File: {template_file}')

        file_input = st.text_input("Enter a source quip file:")

        add_button = st.button("Add to list")

        if add_button:
            if file_input.lower() == "generate":
                st.write("Generating Report")
                final_file_list=""
                for file in st.session_state['file_list'] :
                    final_file_list = final_file_list + " \n " + file    
                #prompt = "Please generate a report with the format described here: " + template_file + " \n Use the content in the following quip files: " + final_file_list 
                prompt = "Analyze the data in this quip: " + final_file_list + "  Perform the following actions: 1/ Exclude the items in column N where Include in MBR is N. 2/ Using Column B, consolidate projects for Hits/Misses/Learnings. 3/ Tag each item with the contributer in Column G 4/ Generate a final report using this template in this quip: " + template_file 
 
            elif len(file_input) > 0:
                st.session_state['file_list'].append(file_input)
            else:
                st.warning("Please Enter a filename")
        st.write("Current List:", st.session_state['file_list'])

if prompt is not None:
    with work_pane.container():
        st.empty()
        st.write(prompt)

    # Create an agent with MCP tools
    with stdio_mcp_client:
        # Get the tools from the MCP server
        tools = stdio_mcp_client.list_tools_sync()
        # Create an agent with these tools
        agent = Agent(model=model, callback_handler=my_callback_handler, tools=tools)

        try: 
            response = agent(prompt)
        except:
            print("Overloaded")
            #print(e)
            time.sleep(60)
            response = agent(prompt)
        #st.write(response)