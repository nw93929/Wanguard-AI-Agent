# AI-Research-Agent

Personal project attempting to build an autonomous AI research agent using LangChain and LangGraph. This agent is designed to navigate complex research tasks by planning, retrieving data from internal and external sources, and self-correcting via a rigorous LLM-based validation loop.

### agents

The brain of the operation. This folder contains the logic for the agent's decision-making process.

graph.py: The core orchestration file. It uses StateGraph to define the nodes (Search, Analyze, Write) and edges (conditional paths) that allow the agent to loop back if research is insufficient.

prompts.py: Contains the system prompts for the "Planner," "Researcher," and "Writer" personas to ensure consistent output quality.

state.py: Defines the TypedDict structure that tracks the agent's memory, research notes, and scoring history throughout a run.

### data

The persistence and schema layer. This folder manages how the agent interacts with physical storage and maintains data integrity.

schemas/: Contains the SQL DDL scripts for Postgres and JSON schema definitions for MongoDB collections to ensure the agent queries the correct fields.

embeddings/: Logic for chunking and vectorizing documents before uploading them to the MongoDB Vector Store.

processed/: A storage area for cached research results or intermediate JSON outputs to prevent redundant API calls and reduce latency.

seed_data/: Sample datasets used to populate the databases during development and for running integration tests.

### evaluation

The quality control layer. This ensures the agent isn't "hallucinating" and meets company standards.

scorer.py: Implements LLM-based scoring using structured output. It evaluates reports based on accuracy, depth, and relevance to X Company’s requirements.

schemas.py: Defines Pydantic models for the validation rubrics, ensuring the "Grader" node returns consistent JSON data.

### services

The integration layer for external data and persistence.

postgres_client.py: Handles connection pooling and natural language-to-SQL querying for internal structured data.

mongo_client.py: Manages the Vector Store interface for unstructured data (e.g., PDF archives) using MongoDB Atlas.

search_tools.py: Wrappers for external search APIs (like Tavily or Brave Search) used for real-time web research.

### workers

The automation layer for production deployment.

scheduler.py: Uses APScheduler or a cron-based trigger to run research tasks at specific intervals (e.g., daily market analysis at 9:00 AM).

tasks.py: Defines specific background tasks that can be offloaded to a queue, allowing the agent to handle multiple research requests concurrently.

### tests

test_graph.py: Unit tests for the LangGraph nodes to ensure the state updates correctly.

test_eval.py: Mock reports passed through the scorer to calibrate the validation thresholds.

### supplementary
config.py: Centralized management for API keys (OpenAI, Anthropic), database URIs, and global hyperparameters (e.g., max research loops).

requirements.txt: List of dependencies including langgraph, langchain-openai, pymongo, and psycopg2-binary.

main.py: The entry point to manually trigger the agent or start the scheduler. 