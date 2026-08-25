from typing import Literal
from pydantic import BaseModel,Field

AgentName=Literal[
    "event_agent",
    "graph_agent"
]

class RouterOutput(BaseModel):
    agents:list[AgentName]=Field(
        description=f"사용자의 질문을 처리하기 위해 실행해야 하는 agent 목록"
    )