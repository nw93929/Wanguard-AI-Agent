from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    query: str
    research_notes: List[str]
    report: str
    score: int  
    iterations: int

def search_node(state: AgentState):
    return {"research_notes": ["Found info on X company"], "iterations": state["iterations"] + 1}

def validator_node(state: AgentState):
    score = 85
    return {"score": score}

# graph
workflow = StateGraph(AgentState)
workflow.add_node("researcher", search_node)
workflow.add_node("validator", validator_node)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "validator")

workflow.add_conditional_edges(
    "validator",
    lambda x: "researcher" if x["score"] < 80 and x["iterations"] < 3 else END
)

research_agent = workflow.compile()