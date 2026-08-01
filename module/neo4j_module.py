from typing import Literal,Any
from collections import defaultdict
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

class Neo4j_Interface:
    def __init__(self,port:int=7687):
        try:
            self.driver=GraphDatabase.driver(
                f"neo4j://127.0.0.1:{port}"
            )
            self.driver.verify_connectivity()
            print("Neo4j 연결 성공")
        except Neo4jError as e:
            print(f"Neo4j error: {e}")

    def connect_db(self,port:int=7687):
        try:
            self.driver=GraphDatabase.driver(
                f"neo4j://127.0.0.1:{port}"
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
            node_type:Literal["class","instance","location"],
            **properties
        ):
        """
        cypher = MERGE로 중복 제거 
        고유 식별자만 MERGE로 전달: node_type + node_id 기준
        나머지 속성은 SET으로 지정

        Input:
            node_id: str node_id
            node_type: "class" or "instance" or "location"
            properties: 노드 속성 키-값
        """
        query=f"""
            MERGE (n:`{node_type}` {{id: $node_id}})
            SET n += $properties
            RETURN n
        """

        with self.driver.session() as session:
            result=session.run(
                query,
                node_id=node_id,
                properties=properties,
            )
            record=result.single() # return 결과에서 레코드 한 개만 가져옴
            if record is None:
                raise RuntimeError(f"node ({node_id},{node_type}) 생성 실패.")
            return record["n"]

    def add_nodes(self,
            nodes:list[dict]
        ):
        """
        List of node_dict
            node:
                node_id: str node_id
                node_type: "class" or "instance" or "location"
                properties: 노드 속성 키-값
        
        node_type별로 묶어서 쿼리를 실행
        """
        nodes_by_type=defaultdict(list)
        for node in nodes:
            node_id=node["node_id"]
            node_type=node["node_type"]
            properties=node.get("properties",{})
            nodes_by_type[node_type].append(
                {
                    "node_id":node_id,
                    "properties":properties,
                }
            )

        created_nodes=[]
        with self.driver.session() as session:
            for node_type,node_list in nodes_by_type.items():
                query=f"""
                    UNWIND $node_list AS node
                    MERGE (n:`{node_type}` {{id: node.id}})
                    SET n += node.properties
                    RETURN n
                """
                try:
                    result=session.run(
                        query,
                        node_list=node_list,
                    )
                    created_nodes.extend(
                        record["n"]
                        for record in result
                    )
                except Neo4jError as e:
                    raise RuntimeError(
                        f"Neo4j 쿼리 실행 실패: {e}"
                    ) from e
        return created_nodes

    def add_edge_event(self,
            src_id:str,
            dst_id:str,
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
        cypher = MERGE로 중복 제거 
        고유 식별자만 MERGE로 전달: edge_type + event_time 기준
        나머지 속성은 SET으로 지정

        Input:
            src_id: str source node_id
            dst_id: str destination node_id
            event_time: ms unix timestamp
            edge_type: "isLocatedIn"||"isOwned"||"isPossessed"||"contains"||"transformTo"
            properties: 노드 속성 키-값
        """

        query=f"""
            MATCH (src {{id: $src_id}})
            MATCH (dst {{id: $dst_id}})
            MERGE (src)-[r:`{edge_type}` {{event_time: $event_time}}]->(dst)
            SET r += $properties
            RETURN r
        """

        with self.driver.session() as session:
            result=session.run(
                query,
                src_id=src_id,
                dst_id=dst_id,
                event_time=event_time,
                properties=properties
            )
            record=result.single()
            if record is None:
                raise RuntimeError(f"edge_event ({src_id}->{dst_id} at {event_time},{edge_type}) 생성 실패.")
            return record["r"]

    def add_edge_events(self,
            edge_events:list[dict]
        ):
        """
        List of edge_event_dict
            edge_event:
                src_id: str source node_id
                dst_id: str destination node_id
                event_time: ms unix timestamp
                edge_type: 
                    "isLocatedIn",
                    "isOwned",
                    "isPossessed",
                    "contains",
                    "transformTo",
                    "isAssociatedWith"
                properties: 노드 속성 키-값
        """
        edge_events_by_type:dict[str,list[dict[str,Any]]]=defaultdict(list)
        for edge_event in edge_events:
            src_id=edge_event["src_id"]
            dst_id=edge_event["dst_id"]
            event_time=edge_event["event_time"]
            edge_type=edge_event["edge_type"]
            properties=edge_event.get("properties",{})
            edge_events_by_type[edge_type].append(
                {
                    "src_id": src_id,
                    "dst_id": dst_id,
                    "event_time": event_time,
                    "properties": properties,
                }
            )

        created_edges=[]
        with self.driver.session() as session:
            for edge_type,edge_list in edge_events_by_type.items():
                query=f"""
                    UNWIND $edge_list AS edge
                    MATCH (src {{id: edge.src_id}})
                    MATCH (dst {{id: edge.dst_id}})
                    MERGE (src)-[r:`{edge_type}` {{
                        event_time: edge.event_time
                    }}]->(dst)
                    SET r += edge.properties
                    RETURN r
                """
                try:
                    result=session.run(
                        query,
                        edge_list=edge_list,
                    )
                    created_edges.extend(
                        record["r"]
                        for record in result
                    )
                except Neo4jError as e:
                    raise RuntimeError(
                        f"Neo4j 쿼리 실행 실패: {e}"
                    ) from e
        return created_edges