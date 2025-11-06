# Music Store Assistant - Multi-Agent Workflow with LangGraph

A comprehensive tutorial demonstrating how to build multi-agent workflows using LangGraph for a customer support system. This example showcases a music store assistant that handles customer inquiries about music catalog and invoice information.

## Overview

This notebook walks through building a production-ready multi-agent system with:

- **Multiple specialized sub-agents** for different tasks
- **Supervisor agent** for intelligent routing
- **Human-in-the-loop** verification
- **Long-term memory** for user preferences
- **Comprehensive evaluations** (final response, single-step, trajectory, multi-turn)

![Architecture](images/architecture.png)

## Features

### Part 1: Building Sub-Agents

1. **Music Catalog Sub-Agent** (ReAct from scratch)
   - Query music catalog (albums, tracks, songs)
   - Search by artist, genre, or song title
   - Personalized recommendations based on user preferences

2. **Invoice Information Sub-Agent** (using LangChain's `create_agent()`)
   - Retrieve customer invoices
   - Sort by date or price
   - Find employee information for support

### Part 2: Multi-Agent Architecture

- **Supervisor Agent**: Routes queries to appropriate sub-agents
- **Human-in-the-Loop**: Verifies customer information before processing
- **Memory Management**: 
  - Short-term: Conversation context within a thread
  - Long-term: Persistent user preferences across sessions

### Part 3: Evaluations

Four comprehensive evaluation strategies:

1. **Final Response**: End-to-end evaluation of agent responses
2. **Single Step**: Unit testing individual agent decisions
3. **Trajectory**: Evaluating the sequence of tool calls
4. **Multi-Turn**: Simulating full conversations with stopping conditions

## Prerequisites

- Python 3.9+
- AWS Account with Bedrock access
- LangSmith account (optional, for evaluations)

## Setup

1. **Clone the repository and navigate to this directory**

```bash
cd langgraph/music-store-assistant
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure AWS credentials**

The notebook uses boto3's default credential chain. You can configure AWS credentials in several ways:

**Option A: AWS CLI (Recommended)**
```bash
aws configure
```

**Option B: Environment variables**

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# Required
AWS_REGION_NAME=us-west-2
AWS_MODEL_ARN=us.anthropic.claude-sonnet-4-20250514-v1:0

# Optional: Uncomment if not using AWS CLI or IAM roles
# AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
# AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
# AWS_SESSION_TOKEN=your_aws_session_token_here

# LangSmith (Optional - for evaluations)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=music-store-assistant
```

**Option C: IAM Roles (Production)**

If running on AWS infrastructure (EC2, ECS, Lambda), attach an appropriate IAM role with Bedrock permissions.

4. **Launch Jupyter Notebook**

```bash
jupyter notebook multi_agent.ipynb
```

## Technologies Used

- **LangGraph**: Agent orchestration and workflow management
- **AWS Bedrock**: Claude Sonnet 4 for LLM capabilities
- **LangChain**: Agent creation and tool management
- **Chinook Database**: Sample SQLite database for music store data
- **LangSmith**: Evaluation and tracing (optional)

## Database

This project uses the [Chinook Database](https://www.sqlitetutorial.net/sqlite-sample-database/), a sample database representing a digital music store with:

- Customer information
- Invoice and purchase history
- Music catalog (artists, albums, tracks)
- Employee information

The database is automatically downloaded and loaded in-memory when running the notebook.

## Key Concepts

### State Management

The agent maintains state across nodes with:
- `messages`: Conversation history
- `customer_id`: Customer identifier
- `loaded_memory`: User preferences from long-term storage
- `remaining_steps`: Recursion limit tracking

### Tools

**Music Catalog Tools:**
- `get_albums_by_artist`: Retrieve albums by artist name
- `get_tracks_by_artist`: Get songs by artist
- `get_songs_by_genre`: Find songs by genre
- `check_for_songs`: Verify song availability

**Invoice Tools:**
- `get_invoices_by_customer_sorted_by_date`: Retrieve invoices by date
- `get_invoices_sorted_by_unit_price`: Sort invoices by price
- `get_employee_by_invoice_and_customer`: Get support rep info

### Multi-Agent Patterns

This implementation uses a **supervisor pattern** where:
- A supervisor agent routes queries to specialized sub-agents
- Sub-agents are called as tools
- Each sub-agent has its own set of specialized tools

## Evaluation Strategies

The notebook includes comprehensive evaluation examples:

1. **Final Response Evaluation**: Measures correctness and professionalism
2. **Single-Step Evaluation**: Tests routing decisions
3. **Trajectory Evaluation**: Validates tool call sequences
4. **Multi-Turn Evaluation**: Simulates full conversations with personas

## Learning Resources

For a deeper dive into LangGraph primitives and framework concepts, check out:
- [LangChain Academy](https://academy.langchain.com/courses/intro-to-langgraph)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## License

This project is part of the sample-agentic-frameworks-on-aws repository.

## Support

For questions or issues, please refer to the main repository documentation or open an issue.
