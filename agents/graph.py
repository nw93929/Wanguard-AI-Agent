from langgraph.graph import StateGraph, END
from .state import AgentState

# Nodes: These would call the prompts and LLMs
def plan_node(state: AgentState):
    return {"plan": ["Check internal DB", "Search Web"], "iteration_count": 1}

def research_node(state: AgentState):
    return {"research_notes": ["Found data point A..."]}

def grade_node(state: AgentState):
    # Logic to check if report is good
    return {"score": 75} 

# workflow orchestration
workflow = StateGraph(AgentState)
workflow.add_node("planner", plan_node)
workflow.add_node("researcher", research_node)
workflow.add_node("grader", grade_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "grader")

# set standard of 80 for report quality
workflow.add_conditional_edges(
    "grader",
    lambda x: "researcher" if x["score"] < 80 else END
)

executable_agent = workflow.compile()