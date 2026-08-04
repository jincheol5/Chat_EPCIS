from typing import Literal
from module import Neo4j_Interface
from langchain.tools import tool

neo4j_interface=Neo4j_Interface()

@tool
def tool_get_num_graph_elements(
        graph_id:str,
        node_type:str|None=None,
        edge_type:str|None=None
    )->dict[str,int]:
    """
    Neo4j 그래프의 노드와 에지 개수를 조회합니다.

    node_type이 주어지면 해당 라벨의 노드만 집계하고,
    edge_type이 주어지면 해당 관계 타입만 집계합니다.
    
    Return:
        dict[str, int]:
            n_node: 조건에 해당하는 노드 개수
            n_edge: 조건에 해당하는 에지 개수

        반환 예시:
            {
                "n_node": 120,
                "n_edge": 350
            }
    """
    return neo4j_interface.get_num_graph_elements(
        graph_id=graph_id,
        node_type=node_type,
        edge_type=edge_type
    )


@tool
def tool_get_node_degree(
        node_id:str,
        graph_id:str,
        direct:Literal[
            "in",
            "out",
            "all"
        ]="all"
    )->int:
    """
    Neo4j 그래프 내의 node_id를 id로 가진 노드의 degree 값을 반환합니다. 

    Return:
        int:
            in-degree or out-degree or all-degree 
    """
    return neo4j_interface.get_node_degree(
        node_id=node_id,
        graph_id=graph_id,
        direct=direct
    )
