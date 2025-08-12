from strands import Agent
from strands.models import BedrockModel
from .tools import search_entities, get_base_details, get_kyc_details


def main():
    """Main entry point for the Probe Strands Agent."""
    model = BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="us-east-1"
    )
    
    agent = Agent(
        model=model,
        tools=[search_entities, get_base_details, get_kyc_details],
        system_prompt="You are a helpful assistant that can search and analyze Indian corporate entities using the Probe42 API. You can search for companies, get basic details, and perform comprehensive KYC analysis."
    )
    
    # Interactive mode
    while True:
        try:
            user_input = input("\nEnter your query (or 'quit' to exit): ")
            if user_input.lower() in ['quit', 'exit']:
                break
            
            response = agent(user_input)
            print(f"\nResponse: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()