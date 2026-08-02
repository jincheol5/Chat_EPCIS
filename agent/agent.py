from langgraph.graph import END, START, StateGraph

from agent.state import GraphState


def process_message(state: GraphState) -> GraphState:
    """입력 메시지를 간단히 처리하는 그래프 노드입니다."""
    return {"message": f"LangGraph가 처리한 메시지: {state['message']}"}


def build_graph():
    """간단한 LangGraph 워크플로를 생성하고 컴파일합니다."""
    workflow = StateGraph(GraphState)

    workflow.add_node("process_message", process_message)
    workflow.add_edge(START, "process_message")
    workflow.add_edge("process_message", END)

    return workflow.compile()


graph = build_graph()


if __name__ == "__main__":
    result = graph.invoke({"message": "안녕하세요!"})
    print(result["message"])
