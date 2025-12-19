from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class GradeSchema(BaseModel):
    score: int = Field(description="Score from 0 to 100")
    critique: str = Field(description="Why this score was given")

def get_report_score(report_content):
    llm = ChatOpenAI(model="gpt-4o")
    # Forces the AI to follow the GradeSchema exactly
    structured_llm = llm.with_structured_output(GradeSchema)
    return structured_llm.invoke(report_content)