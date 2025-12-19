import pytest
from agents.graph import workflow

def test_workflow_logic():
    # We provide a fake state with a low score
    initial_state = {"task": "test", "score": 10, "iteration_count": 0}
    
    # We check if the next step is 'researcher' (the loop-back)
    # This ensures our "Conditional Edges" are working
    graph = workflow.compile()
    next_step = graph.get_next_step(initial_state)
    assert next_step == "researcher"