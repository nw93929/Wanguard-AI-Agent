"""
Agent State Definition
======================

This file defines the "memory" structure shared across all nodes in the agent graph.

## For ML/DS Engineers:

### What is State in LangGraph?
Think of state like the activations that flow through a neural network, except:
- In neural networks: Tensors flow forward through layers
- In agent graphs: A dictionary flows through nodes, getting updated at each step

### Why TypedDict?
TypedDict provides static type checking without runtime overhead:
- Catches bugs at development time (e.g., typos in key names)
- Provides IDE autocomplete
- Documents the expected structure
- No performance cost (it's just a dict at runtime)

### The operator.add Pattern
```python
research_notes: Annotated[List[str], operator.add]
```

This tells LangGraph to **accumulate** updates instead of replacing them.

Without operator.add:
  Node 1 returns: {"research_notes": ["Fact A"]}
  State becomes: {"research_notes": ["Fact A"]}

  Node 2 returns: {"research_notes": ["Fact B"]}
  State becomes: {"research_notes": ["Fact B"]}  # Fact A lost!

With operator.add:
  Node 1 returns: {"research_notes": ["Fact A"]}
  State becomes: {"research_notes": ["Fact A"]}

  Node 2 returns: {"research_notes": ["Fact B"]}
  State becomes: {"research_notes": ["Fact A", "Fact B"]}  # Both facts preserved!

This is crucial for iterative research where each loop adds more context.

### State Lifecycle Example:
```
Initial State:
{
  "task": "Analyze Apple stock",
  "plan": [],
  "research_notes": [],
  "report": None,
  "score": 0,
  "loop_count": 0
}

After Planner Node:
{
  "task": "Analyze Apple stock",
  "plan": ["Check revenue", "Analyze P/E ratio", "Review debt levels"],
  "research_notes": [],
  "report": None,
  "score": 0,
  "loop_count": 1  # Incremented
}

After Researcher Node (First Loop):
{
  "task": "Analyze Apple stock",
  "plan": ["Check revenue", ...],
  "research_notes": ["Apple Q4 2024 revenue: $89.5B"],  # Added
  "report": None,
  "score": 0,
  "loop_count": 1
}

After Writer Node:
{
  "task": "Analyze Apple stock",
  "plan": ["Check revenue", ...],
  "research_notes": ["Apple Q4 2024 revenue: $89.5B"],
  "report": "# Apple Stock Analysis\\n\\n## Financial Performance\\n...",  # Generated
  "score": 0,
  "loop_count": 1
}

After Grader Node:
{
  "task": "Analyze Apple stock",
  "plan": ["Check revenue", ...],
  "research_notes": ["Apple Q4 2024 revenue: $89.5B"],
  "report": "# Apple Stock Analysis...",
  "score": 72,  # Below threshold!
  "loop_count": 1
}

Decision: score (72) < 85 → Loop back to Researcher

After Researcher Node (Second Loop):
{
  "task": "Analyze Apple stock",
  "plan": ["Check revenue", ...],
  "research_notes": [
    "Apple Q4 2024 revenue: $89.5B",  # Previous research preserved
    "Apple P/E ratio: 28.3, Operating margin: 30.1%"  # New research added
  ],
  "report": "# Apple Stock Analysis...",  # Will be regenerated
  "score": 72,
  "loop_count": 1
}

... cycle continues until score >= 85 or loop_count >= 3
```
"""

import operator
from typing import Annotated, List, TypedDict, Optional

class AgentState(TypedDict):
    """
    The shared memory structure for the research agent workflow.

    This state object is passed through all nodes in the graph. Each node can read
    from it and return updates that get merged back in.

    Attributes:
    -----------
    task : str
        The original user query/research question.
        Set once at the beginning, never modified.
        Example: "Analyze Tesla's Q4 2024 financial performance"

    plan : List[str]
        The research strategy created by the Planner node.
        Contains the breakdown of steps to execute.
        Example: ["Analyze revenue trends", "Review profit margins", "Assess debt levels"]

    context : Annotated[List[str], operator.add]
        DEPRECATED/UNUSED in current implementation.
        Originally intended for general contextual information.
        Kept for backward compatibility but not actively used.

    research_notes : Annotated[List[str], operator.add]
        Accumulated research findings from the Researcher node.
        Uses operator.add to APPEND new findings rather than replace.

        Each entry typically contains:
        - Specific data points (numbers, metrics)
        - Time period context (Q3 2024, FY 2023)
        - Source attribution (SEC filing, earnings call)

        Example after 2 research loops:
        [
          "Retrieved Context: Tesla Q3 2024 revenue $25.2B, up 8% YoY...",
          "Retrieved Context: Tesla gross margin 19.8%, down from 25.1% in Q3 2023..."
        ]

    report : Optional[str]
        The final markdown-formatted research report from the Writer node.
        None until the Writer node executes.
        Contains structured analysis with sections for financials, valuation, risks.

    score : int
        Quality score (0-100) assigned by the Grader node.
        Used in the conditional routing logic to determine if another research loop is needed.

        Scoring rubric (see prompts.py for details):
        - 0-70: Poor quality, needs significant improvement
        - 70-84: Acceptable but below threshold, trigger another research loop
        - 85-100: High quality, meets publication standards

    loop_count : int
        Iteration counter tracking how many times the Planner node has executed.
        Used as a safety mechanism to prevent infinite loops.

        Max loops = 3 (configurable in decide_to_end() function in graph.py)

        Why 3 loops?
        - Loop 1: Initial broad research
        - Loop 2: Fill in gaps identified by grader
        - Loop 3: Final refinement attempt
        - After 3: Diminishing returns, return best effort

    Type System Details:
    -------------------
    - TypedDict: Provides type hints without runtime overhead
    - Annotated[List[str], operator.add]: Type hint + metadata for accumulation behavior
    - Optional[str]: Can be None (report doesn't exist until Writer runs)

    Design Decisions:
    -----------------
    1. Why not use a dataclass or Pydantic model?
       - LangGraph requires TypedDict for its state merging logic
       - TypedDict is dict-compatible, easy to serialize/deserialize

    2. Why separate plan vs research_notes?
       - plan: Strategic (what to do)
       - research_notes: Tactical (what we found)
       - Separation allows tracking strategy vs execution

    3. Why track loop_count here instead of in the graph?
       - State is persistent across graph executions
       - Allows resuming workflows from checkpoints
       - Makes the iteration limit visible to all nodes
    """

    task: str
    plan: List[str]  # steps to take created by Planner
    context: Annotated[List[str], operator.add]  # operator.add so new context is appended, not overwritten
    research_notes: Annotated[List[str], operator.add]
    report: Optional[str]
    score: int  # quality score (0-100) from Grader
    loop_count: int  # Track iterations to prevent infinite loops
