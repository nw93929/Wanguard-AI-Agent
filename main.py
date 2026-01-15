"""
AI Research Agent Entry Point
==============================

This is the main execution file for an autonomous financial research agent built with LangGraph.

## For Data Scientists New to AI Agents:

### What is LangGraph?
LangGraph is a framework for building stateful, multi-actor applications with LLMs.
It's built on concepts from graph theory:
- **Nodes**: Individual functions (our "agents" like Planner, Writer, Grader)
- **Edges**: Transitions between nodes
- **State**: Shared memory that flows through the graph (like a dict passed between functions)
- **Conditional Edges**: Decision points (if score < 85, loop back to research)

### What is RAG (Retrieval Augmented Generation)?
Instead of relying solely on the LLM's training data, RAG:
1. Takes your query
2. Searches a vector database (Pinecone) for relevant documents
3. Injects that context into the LLM prompt
4. Gets more accurate, source-backed responses

Vector databases work like this:
- Documents are converted to embeddings (high-dimensional vectors)
- Similar documents cluster together in vector space
- Queries are also embedded and matched to nearest neighbors (cosine similarity)

### This Agent's Workflow:
1. **Planner Node**: Breaks down the research task into steps (like a project manager)
2. **Researcher Node**: Queries Pinecone vector store for relevant financial data
3. **Writer Node**: Synthesizes research into a professional markdown report
4. **Grader Node**: Scores the report (0-100) using a local quantized model
5. **Conditional Loop**: If score < 85 and loops < 3, go back to step 2

This is called a "Plan-Execute-Review" loop.
"""

import asyncio
from agents.graph import app
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables (API keys, database URIs) from .env file
load_dotenv()

async def run_research(user_query: str):
    """
    Executes the research agent workflow asynchronously.

    Args:
        user_query: The research question or stock analysis task

    How it works:
    -------------
    1. Creates a unique thread_id for this execution (like a session ID)
    2. Initializes the agent's "state" - shared memory for all nodes
    3. Streams through the graph nodes, printing progress
    4. Returns the final research report

    The State Pattern:
    ------------------
    State is a TypedDict that flows through all nodes. Each node can:
    - Read from state (e.g., access the original query)
    - Write to state (e.g., add research notes)
    - Return updates that get merged into state

    Think of it like this:
        state = {"task": "Analyze AAPL", "research_notes": []}

        # Planner node runs
        state updates with {"plan": ["Step 1", "Step 2"]}
        # Now state = {"task": "...", "research_notes": [], "plan": ["Step 1", "Step 2"]}

        # Researcher node runs
        state updates with {"research_notes": ["AAPL revenue: $394B"]}
        # State merges the new research notes with existing ones

    Streaming vs Invoke:
    --------------------
    - app.invoke(state): Runs entire graph, returns final state (synchronous feel)
    - app.astream(state): Yields updates as each node completes (async, observable)

    We use streaming here so we can print progress in real-time.
    """

    # Unique thread_id allows LangGraph to track this execution in memory
    # If we used the same thread_id, it would resume from previous state
    config = {"configurable": {"thread_id": str(uuid4())}}

    # Initialize the agent state - this is the "memory" shared across all nodes
    initial_state = {
        "task": user_query,           # The original research question
        "plan": [],                   # Will be populated by Planner node
        "research_notes": [],         # Accumulated by Researcher node (additive)
        "report": None,               # Final output from Writer node
        "loop_count": 0,              # Iteration counter (prevents infinite loops)
        "score": 0                    # Quality score from Grader node (0-100)
    }

    print(f"--- Starting Research for: {user_query} ---")

    # Stream through the graph - yields events as each node completes
    # stream_mode="updates" means we only see the NEW updates, not the full state each time
    async for event in app.astream(initial_state, config, stream_mode="updates"):
        # event is a dict: {node_name: output_from_that_node}
        for node_name, output in event.items():
            print(f"\n[Node Execution] Finished: {node_name}")

            # Optional: Print specific updates for debugging
            if "research_notes" in output:
               print(f" -> Found {len(output['research_notes'])} new facts.")
            if "score" in output:
                print(f" -> Quality score: {output['score']}/100")

    # After the graph completes, fetch the final consolidated state
    # This is necessary because streaming only gives us updates, not the full final state
    final_state = await app.aget_state(config)
    report = final_state.values.get("report")

    # Display results
    if report:
        print("\n" + "="*50)
        print("FINAL RESEARCH REPORT")
        print("="*50 + "\n")
        print(report)
    else:
        print("\n[Error] No report was generated. Check your node logic.")

if __name__ == "__main__":
    # Example query - you can modify this to research any stock or financial topic
    query = "Research the impact of generative AI on PostgreSQL performance optimization."

    try:
        # Print the graph structure in ASCII art (helpful for debugging)
        print("Agent Workflow Graph:")
        print("=" * 50)
        print(app.get_graph().print_ascii())
        print("=" * 50 + "\n")

        # Run the agent (asyncio.run handles the event loop for us)
        asyncio.run(run_research(query))
    except KeyboardInterrupt:
        print("\nResearch cancelled by user.")
