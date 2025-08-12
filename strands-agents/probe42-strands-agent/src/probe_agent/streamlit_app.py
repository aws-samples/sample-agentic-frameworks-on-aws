import streamlit as st
import os
from strands import Agent
from strands.models import BedrockModel
from tools import search_entities, get_base_details, get_kyc_details


@st.cache_resource
def get_agent():
    """Initialize and cache the Strands agent."""
    # Check for required environment variables
    if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
        st.error("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        st.stop()
    
    model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="us-east-1"
    )
    
    return Agent(
        model=model,
        tools=[search_entities, get_base_details, get_kyc_details],
        system_prompt="You are a helpful assistant that can search and analyze Indian corporate entities using the Probe42 API. You can search for companies, get basic details, and perform comprehensive KYC analysis."
    )


def main():
    st.title("🏢 Probe Corporate Intelligence")
    st.write("Search and analyze Indian corporate entities using AI")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about Indian companies..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    agent = get_agent()
                    response = agent(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Sidebar with examples
    with st.sidebar:
        st.header("💡 Example Queries")
        
        examples = [
            "Search for companies starting with 'Tata'",
            "Get base details for CIN U73100KA2005PTC036337",
            "Show KYC details for L65923DL1982PLC013915",
            "Find Reliance companies and show their details"
        ]
        
        for example in examples:
            if st.button(example, key=example):
                st.session_state.messages.append({"role": "user", "content": example})
                st.rerun()


if __name__ == "__main__":
    main()