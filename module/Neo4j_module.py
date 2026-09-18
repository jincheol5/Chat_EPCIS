from typing import Literal,Any
from collections import defaultdict
from tqdm import tqdm
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

class Neo4j_Interface:
    def __init__(self,port:int=7687):
        self.connect_db(port=port)

    def connect_db(self,port:int=7687):
        try:
            self.driver=GraphDatabase.driver(
                f"neo4j://127.0.0.1:{port}",
                auth=("neo4j","11111111")
            )
            self.driver.verify_connectivity()
            print("Neo4j 연결 성공")
        except Neo4jError as e:
            print(f"Neo4j error: {e}")

    def disconnect_db(self):
        if self.driver is not None:
            self.driver.close()
            self.driver=None
            print("Neo4j database disconnected!")

    def add_node(self,
            node_id:str,
            graph_id:str,
            node_type:Literal["class","instance","location"],
            **properties
        ):
        """
        {} : Python f-string 문자열 치환
        $  : Cypher parameter binding

        node_type은 Label이므로 f-string으로 삽입하고,
        property 값은 Cypher parameter로 전달합니다.
        """
        query=f"""
            MERGE (n:{node_type}
                {{
                    id:$node_id,
                    graph_id:$graph_id
                }}
            )
            SET n+=$properties
        """
        params={
            "node_id":node_id,
            "graph_id":graph_id,
            "properties":properties
        }
        try:
            self.driver.execute_query(
                query_=query,
                parameters_=params
            )
        except Neo4jError as e:
            print(f"Neo4j error: {e}")

    def add_node_list(self,
            graph_id:str,
            node_list:list[dict]
        ):
        """
        여러 개의 노드를 Neo4j에 한 번에 추가
        Label은 Cypher parameter로 전달할 수 없으므로 node_type별로 나누어서 처리
        """
        node_type_dict={}
        for node in node_list:
            node_type=node["node_type"]
            node_id=node["node_id"]

            # node_id, node_type을 제외한 나머지를 property로 사용
            properties={
                key:value
                for key,value in node.items()
                if key not in ["node_id","node_type"]
            }
            node_type_dict.setdefault(node_type,[]).append(
                {
                    "node_id": node_id,
                    "properties": properties
                }
            )

        # node_type별 nodes insert
        for node_type,nodes in node_type_dict.items():
            query=f"""
                UNWIND $nodes AS node
                MERGE (n:{node_type}
                {{
                    id:node.node_id,
                    graph_id:$graph_id
                }}
                SET n+=node.properties
            )
            """
            params={
                "graph_id":graph_id,
                "nodes":nodes
            }
            try:
                self.driver.execute_query(
                    query_=query,
                    parameters_=params
                )
            except Neo4jError as e:
                print(f"Neo4j error: {e}")

    def add_edge(self,
            src_id:str,
            dst_id:str,
            graph_id:str,
            event_time:int,
            edge_type:Literal[
                "isLocatedIn",
                "isOwned",
                "isPossessed",
                "contains",
                "transformTo",
                "isAssociatedWith"
            ],
            **properties
        ):
        """
        고유 식별자만 MERGE로 전달: edge_type + event_time이 다르면 같은 src->dst 있어도 새로 생성
        나머지 속성은 SET으로 지정

        Input:
            src_id: str source node_id
            dst_id: str destination node_id
            event_time: ms unix timestamp
            edge_type: "isLocatedIn"||"isOwned"||"isPossessed"||"contains"||"transformTo"
            properties: 노드 속성 키-값
        """
        query=f"""
            MATCH (src 
                {{
                    id:$src_id,
                    graph_id:$graph_id
                }}
            )
            MATCH (dst 
                {{
                    id:$dst_id,
                    graph_id:$graph_id
                }}
            )
            MERGE (src)-[r:{edge_type} 
                {{
                    event_time:$event_time,
                    graph_id:$graph_id
                }}
            ]->(dst)
            SET r+=$properties
        """
        params={
            "src_id":src_id,
            "dst_id":dst_id,
            "graph_id":graph_id,
            "event_time":event_time,
            "properties":properties
        }
        try:
            self.driver.execute_query(
                query_=query,
                parameters_=params
            )
        except Neo4jError as e:
            print(f"Neo4j error: {e}")

    def add_edge_list(self,
            graph_id:str,
            edge_list:list[dict]
        ):
        """
        """
        edge_type_dict={}
        for edge in edge_list:
            edge_type=edge["edge_type"]
            src_id=edge["src_id"]
            dst_id=edge["dst_id"]
            event_time=edge["event_time"]

            properties={
                key:value
                for key,value in edge.items()
                    if key not in [
                        "src_id",
                        "dst_id",
                        "edge_type",
                        "event_time"
                    ]
            }
            edge_type_dict.setdefault(edge_type,[]).append(
                {
                    "src_id":src_id,
                    "dst_id":dst_id,
                    "event_time":event_time,
                    "properties":properties
                }
            )
        
        for edge_type,edges in edge_type_dict.items():
            query=f"""
                UNWIND $edges AS edge
                MATCH (src 
                    {{
                        id:edge.src_id,
                        graph_id:$graph_id
                    }}
                )
                MATCH (dst 
                    {{
                        id:edge.dst_id,
                        graph_id:$graph_id
                    }}
                )
                MERGE (src)-[r:{edge_type} 
                    {{
                        event_time:$event_time,
                        graph_id:$graph_id
                    }}
                ]->(dst)
                SET r+=edge.properties
            """
            params={
                "graph_id":graph_id,
                "edges":edges
            }
            try:
                self.driver.execute_query(
                    query_=query,
                    parameters_=params
                )
            except Neo4jError as e:
                print(f"Neo4j error: {e}")

    def delete_graph(self,
            graph_id:str
        ):
        """
        특정 graph_id에 속한 모든 node와 edge 삭제
        """
        query=f"""
            MATCH (n 
                {{
                    graph_id:$graph_id
                }}
            )
            DETACH DELETE n
        """
        params={
            "graph_id": graph_id
        }
        try:
            self.driver.execute_query(
                query_=query,
                parameters_=params
            )
        except Neo4jError as e:
            print(f"Neo4j error: {e}")

    def get_num_graph_element(self,
            graph_id:str,
            node_type:Literal["class","instance","location"]|None=None,
            edge_type:Literal[
                "isLocatedIn",
                "isOwned",
                "isPossessed",
                "contains",
                "transformTo",
                "isAssociatedWith"
            ]|None=None
        ):
        """
        특정 graph_id에 속한 모든 node와 edge 개수 반환

        node_type이 주어진 경우:
            해당 type의 node 개수만 반환

        edge_type이 주어진 경우:
            해당 type의 edge 개수만 반환
        """
        # node type 조건
        if node_type is None:
            node_pattern=f"(n {{graph_id:$graph_id}})"
        else:
            node_pattern=f"(n:{node_type} {{graph_id:$graph_id}})"

        # edge type 조건
        if edge_type is None:
            edge_pattern=f"[r {{graph_id:$graph_id}}]"
        else:
            edge_pattern=f"[r:{edge_type} {{graph_id:$graph_id}}]"


        query=f"""
            MATCH {node_pattern}
            WITH count(n) AS n_node
            OPTIONAL MATCH ()-{edge_pattern}->()
            RETURN n_node,count(r) AS n_edge
        """
        params={
            "graph_id":graph_id
        }
        try:
            records,_,_=self.driver.execute_query(
                query_=query,
                parameters_=params
            )
            if not records:
                return {
                    "n_node":0,
                    "n_edge":0
                }
            return{
                "n_node":records[0]["n_node"],
                "n_edge": records[0]["n_edge"]
            }
        except Neo4jError as e:
            print(f"Neo4j error: {e}")
            return {
                "n_node":0,
                "n_edge":0
            }

    def get_node_degree(self,
            node_id:str,
            graph_id:str,
            direction:Literal[
                "in",
                "out"
            ]="in",
        ):
        """
        특정 graph_id에 속한 node_id 를 가지는 node의 in/out degree 반환 
        """
        if direction=="in":
            edge_pattern=f"<-[r {{graph_id:$graph_id}}]-"
        if direction=="out":
            edge_pattern=f"-[r {{graph_id:$graph_id}}]->"

        query=f"""
            MATCH (n 
                {{
                    id: $node_id,
                    graph_id: $graph_id
                }}
            )
            OPTIONAL MATCH (n){edge_pattern}()
            RETURN count(r) AS degree
        """
        params={
            "node_id":node_id,
            "graph_id":graph_id
        }
        try:
            records,_,_=self.driver.execute_query(
                query_=query,
                parameters_=params
            )
            if not records:
                return 0
            return records[0]["degree"]
        except Neo4jError as e:
            print(f"Neo4j error: {e}")
            return 0
