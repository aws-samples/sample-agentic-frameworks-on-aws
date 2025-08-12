# Probe Strands Agent

A Strands Agent implementation for accessing Probe42 API to search and analyze Indian corporate entities.

[Probe API Portal](https://apiportal.probe42.in/#/portal/explore-api)

**Note**: Probe42 API has pricing. Check their documentation for current rates.

## Features

- `search_entities`: Search within the database of all Indian corporates by name
- `get_base_details`: Get essential data points about a corporate entity for verification
- `get_kyc_details`: Fast-track corporate KYC with comprehensive regulatory data

## Setup

1. Set your Probe42 API key as an environment variable:
```bash
export PROBE_API_KEY="your_api_key_here"
```

2. Configure AWS credentials for Bedrock access (recommended to use role based access).

3. Install dependencies:
```bash
uv sync
```

4. Run the agent:
```bash
uv run probe-agent
```

## Usage

### Command Line
Run the interactive agent:
```bash
uv run probe-agent
```

### Streamlit Web Interface
Run the web application:
```bash
# Ensure environment variables are set
export PROBE_API_KEY="your_api_key_here"

cd src/probe_agent
streamlit run streamlit_app.py
```

You can ask questions like:

### Search Entities
```
Search for companies starting with "Tata"
Find entities with name beginning with "Reliance"
Show me companies that start with "Infosys"
```

### Base Details
```
Get base details for CIN U73100KA2005PTC036337
Show me basic information for entity L65923DL1982PLC013915
What are the base details of U72900KA2001PTC028925?
```

### KYC Details
```
Get KYC details for U73100KA2005PTC036337
Show me comprehensive KYC data for L65923DL1982PLC013915
What's the Probe Score and director information for U72900KA2001PTC028925?
```

## Architecture

Built using the Strands Agent SDK:
- **Tools**: Python functions decorated with `@tool` for automatic schema generation
- **Agent**: Strands Agent with system prompt and tool integration
- **API Client**: Async HTTP client using httpx for Probe42 API calls

## License

Apache License 2.0
