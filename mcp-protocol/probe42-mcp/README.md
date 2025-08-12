# Probe MCP Server

A Model Context Protocol (MCP) server implementation that provides access to Probe42 API for searching Indian corporate entities.

[Probe API Portal](https://apiportal.probe42.in/#/portal/explore-api)

## Features

- `search_entities`: Search within the database of all Indian corporates by name
- `get_base_details`: Get essential data points about a corporate entity for verification
- `get_kyc_details`: Fast-track corporate KYC with comprehensive regulatory data

## Setup

1. Set your Probe42 API key as an environment variable:
```bash
export PROBE_API_KEY="your_api_key_here"
```

2. Install dependencies:
```bash
uv sync
```

## Usage with Amazon Q Developer

Add the following configuration to Amazon Q config:

```json
{
  "mcpServers": {
    "probe": {
      "command": "uv",
      "args": [
        "--directory",
        "/<folder>/probe-mcp-mvp",
        "run",
        "probe-mcp-server"
      ],
      "env": {
        "PROBE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Test Prompts

### Search Entities
```
Search for companies starting with "Tata"
```
```
Find entities with name beginning with "Reliance"
```
```
Show me companies that start with "Infosys"
```

### Base Details
```
Get base details for CIN U73100KA2005PTC036337
```
```
Show me basic information for entity L65923DL1982PLC013915
```
```
What are the base details of U72900KA2001PTC028925?
```

### KYC Details
```
Get KYC details for U73100KA2005PTC036337
```
```
Show me comprehensive KYC data for L65923DL1982PLC013915
```
```
What's the Probe Score and director information for U72900KA2001PTC028925?
```