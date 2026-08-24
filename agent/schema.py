from typing import Literal
from pydantic import BaseModel

class AgentRouterOutput(BaseModel):
    tool_agent:Literal[
        "event_agent",
        "graph_agent"
    ]