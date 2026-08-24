from typing import Literal
from langgraph.graph import MessagesState
from .schema import AgentName

class ChatEPCISState(MessagesState):
    # Router가 결정한 실행 대상
    agent_queue:list[AgentName]

    # 현재 실행 중인 agent
    current_agent:AgentName|None

    # 각 agent의 처리 결과
    agent_results:list[str]