# LangGraph Memory Patterns

This repository demonstrates practical implementations of hierarchical memory, consolidation, and semantic retrieval patterns using LangGraph within an automotive service assistant use case.

## Overview

This project showcases how to implement different memory patterns for LLM-powered agents, specifically focusing on:
- Hierarchical memory structures
- Memory consolidation techniques
- Semantic retrieval methods
- Integration with LangGraph for agent orchestration

## Features

- **Multi-tier Memory Architecture**
  - Short-term memory (Checkpointer)
  - Episodic memory store
  - Long-term memory store
  - Semantic retrieval capabilities

- **Automotive Service Use Case**
  - Vehicle service diagnosis
  - Repair history tracking
  - Cost estimation
  - Customer interaction management


## Key Components

1. **Memory Stores**
   - CheckPointerInMemory
   - EpisodicStoreFile
   - LongTermStoreFile

2. **Retrievers**
   - SemanticStoreRetrieval
   - GraphRetrieval

3. **Tools**
   - AutomotiveKnowledgeToolkit
   - RepairCostEstimate

4. **Memory Orchestration**
   - MultiTierMemoryOrchestrator
   - Consolidator for memory optimization

## Usage

The notebook demonstrates:
1. Initializing memory stores
2. Creating and managing sessions
3. Storing and retrieving diagnostic data
4. Implementing memory consolidation
5. Using LangGraph for agent workflow orchestration

## Testing Environment

This notebook was tested on SageMaker Studio Jupyter Lab.

