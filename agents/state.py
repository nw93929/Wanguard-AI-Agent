from typing import Annotated, List, TypedDict
from operator import add

class AgentState(TypedDict):
    # The user's original question
    task: str 
    # A list of steps the agent decided to take
    plan: List[str]
    # A list where new research notes are appended (added) over time
    research_notes: Annotated[List[str], add] 
    # The final written document
    report: str
    # The quality score from the grader (0-100)
    score: int
    # How many times we have tried to research (to prevent infinite loops)
    iteration_count: int