from typing import Literal,Any
from collections import defaultdict
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

class Neo4j_Interface:
    def __init__(self,port:int=7687):
        try:
            self.driver=GraphDatabase.driver(
                f"neo4j://127.0.0.1:{port}",
                auth=("neo4j","11111111")
            )
            self.driver.verify_connectivity()
            print("Neo4j 연결 성공")
        except Neo4jError as e:
            print(f"Neo4j error: {e}")

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

    def delete_graph(self,
            graph_id:str
        ):
        """
        Neo4j의 특정 graph의 노드와 관계를 삭제
        """
        query=f"""
            MATCH (n {{graph_id: $graph_id}})
            DETACH DELETE n;
        """
        with self.driver.session() as session:
            session.run(query,graph_id=graph_id).consume()
        print(f"Delete graph elements: {graph_id}")

    def delete_specific_graph(self,
            graph_id:str
        ):
        """
        Neo4j의 특정 graph의 노드와 관계를 삭제
        """
        self.delete_graph(graph_id=graph_id)

    def add_node(self,
            node_id:str,
            graph_id:str,
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
            MERGE (n:`{node_type}` {{id: $node_id, graph_id: $graph_id}})
            SET n += $properties
            SET n.graph_id = $graph_id
            RETURN n
        """

        with self.driver.session() as session:
            result=session.run(
                query,
                node_id=node_id,
                graph_id=graph_id,
                properties=properties,
            )
            record=result.single() # return 결과에서 레코드 한 개만 가져옴
            if record is None:
                raise RuntimeError(f"node ({node_id},{node_type}) 생성 실패.")
            return record["n"]

    def add_nodes(self,
            graph_id:str,
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
                    MERGE (n:`{node_type}` {{
                        id: node.node_id,
                        graph_id: $graph_id
                    }})
                    SET n += node.properties
                    SET n.graph_id = $graph_id
                    RETURN n
                """
                try:
                    result=session.run(
                        query,
                        graph_id=graph_id,
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
        print(f"nodes input successful!")
        return created_nodes

    def add_edge_event(self,
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
            MATCH (src {{id: $src_id, graph_id: $graph_id}})
            MATCH (dst {{id: $dst_id, graph_id: $graph_id}})
            MERGE (src)-[r:`{edge_type}` {{
                event_time: $event_time,
                graph_id: $graph_id
            }}]->(dst)
            SET r += $properties
            SET r.graph_id = $graph_id
            RETURN r
        """

        with self.driver.session() as session:
            result=session.run(
                query,
                src_id=src_id,
                dst_id=dst_id,
                graph_id=graph_id,
                event_time=event_time,
                properties=properties
            )
            record=result.single()
            if record is None:
                raise RuntimeError(f"edge_event ({src_id}->{dst_id} at {event_time},{edge_type}) 생성 실패.")
            return record["r"]

    def add_edge_events(self,
            graph_id:str,
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
                    MATCH (src {{id: edge.src_id, graph_id: $graph_id}})
                    MATCH (dst {{id: edge.dst_id, graph_id: $graph_id}})
                    MERGE (src)-[r:`{edge_type}` {{
                        event_time: edge.event_time,
                        graph_id: $graph_id
                    }}]->(dst)
                    SET r += edge.properties
                    SET r.graph_id = $graph_id
                    RETURN r
                """
                try:
                    result=session.run(
                        query,
                        graph_id=graph_id,
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
        print(f"edge_events input successful!")
        return created_edges

    def get_num_graph_elements(self,
            graph_id:str,
            node_type:str=None,
            edge_type:str=None
        ):
        """
        """
        node_pattern=(
            f"(n:`{node_type}`)"
            if node_type is not None
            else "(n)"
        )
        edge_pattern=(
            f"()-[r:`{edge_type}`]->()"
            if edge_type is not None
            else "()-[r]->()"
        )

        query=f"""
            CALL {{
                MATCH {node_pattern}
                WHERE n.graph_id = $graph_id
                RETURN count(n) AS node_count
            }}
            CALL {{
                MATCH {edge_pattern}
                WHERE r.graph_id = $graph_id
                RETURN count(r) AS edge_count
            }}
            RETURN node_count, edge_count
        """
        with self.driver.session() as session:
            record=session.run(query,graph_id=graph_id).single()
            if record is None:
                return {
                    "n_node": 0,
                    "n_edge": 0,
                }
            return {
                "n_node": record["node_count"],
                "n_edge": record["edge_count"],
            }

    def get_node_degree(self,
            node_id:str,
            graph_id:str,
            direct:Literal[
                "in",
                "out",
                "all"
            ]="all"
        )->int:
        """
        특정 노드의 degree를 반환합니다.

        Return:
            degree of node: int
        """
        if direct=="in":
            relation_pattern=f"<-[r]-()"
        elif direct=="out":
            relation_pattern=f"-[r]->()"
        elif direct=="all":
            relation_pattern=f"-[r]-()"
        else:
            raise ValueError(
                f"direct는 'in', 'out', 'all' 중 하나여야 합니다: {direct}"
            )

        query=f"""
            MATCH (n {{id: $node_id, graph_id: $graph_id}})
            OPTIONAL MATCH (n){relation_pattern}
            WHERE r.graph_id = $graph_id
            RETURN count(r) AS degree
        """

        with self.driver.session() as session:
            record=session.run(
                query,
                node_id=node_id,
                graph_id=graph_id,
            ).single()
            if record is None:
                return 0
            return record["degree"]

    def get_trace_events(self,
            node_id:str,
            graph_id:str,
            direction:Literal[
                "forward",
                "backward",
                "both",
            ],
            max_depth:int|None=5
        )->list[str]:
        """
        특정 노드에서 시작하여 관련 노드 ID를 추적.
        시작 노드 ID도 반환 목록에 포함.
        시작 노드에서 갈 수 있는 경로를 Neo4j가 한꺼번에 찾고, 그중 방향과 시간 순서가 올바른 경로만 남김.
        direction이 both이면 forward 또는 backward 조건을 만족하는 노드를 함께 조회하고 중복을 제거.
        하나의 Cypher 쿼리로 시간 순서를 유지하며 관련 노드 ID를 탐색.
        시작 노드에서 최대 깊이까지 가능한 경로를 찾은 뒤, 경로 전체가 방향과 시간 조건을 만족하는지 검사.

        forward:
            transformTo: input -> output
            contains/isAssociatedWith: child -> parent
        backward:
            transformTo: output -> input
            contains/isAssociatedWith: parent -> child
        """
        path_range="0.." if max_depth is None else f"0..{max_depth}"
        forward_condition="""
            all(i IN range(0,size(relationships(path))-1) WHERE
                (type(relationships(path)[i]) = 'transformTo'
                    AND startNode(relationships(path)[i]) = nodes(path)[i])
                OR
                (type(relationships(path)[i]) IN ['contains','isAssociatedWith']
                    AND endNode(relationships(path)[i]) = nodes(path)[i])
            )
            AND all(i IN range(0,size(relationships(path))-2) WHERE
                relationships(path)[i].event_time
                    < relationships(path)[i+1].event_time
            )
        """
        backward_condition="""
            all(i IN range(0,size(relationships(path))-1) WHERE
                (type(relationships(path)[i]) = 'transformTo'
                    AND endNode(relationships(path)[i]) = nodes(path)[i])
                OR
                (type(relationships(path)[i]) IN ['contains','isAssociatedWith']
                    AND startNode(relationships(path)[i]) = nodes(path)[i])
            )
            AND all(i IN range(0,size(relationships(path))-2) WHERE
                relationships(path)[i].event_time
                    > relationships(path)[i+1].event_time
            )
        """

        if direction=="forward":
            trace_condition=forward_condition
        elif direction=="backward":
            trace_condition=backward_condition
        else:
            trace_condition=(
                f"(({forward_condition}) OR ({backward_condition}))"
            )

        query=f"""
            MATCH path=(start {{
                id: $node_id,
                graph_id: $graph_id
            }})-[*{path_range}]-(target {{graph_id: $graph_id}})
            WHERE all(relation IN relationships(path) WHERE
                relation.graph_id = $graph_id
            )
                AND ({trace_condition})
            WITH target.id AS node_id,
                min(length(path)) AS depth
            RETURN node_id
            ORDER BY depth ASC,node_id ASC
        """
        with self.driver.session() as session:
            result=session.run(
                query,
                node_id=node_id,
                graph_id=graph_id,
            )
            return [
                record["node_id"]
                for record in result
                if record["node_id"] is not None
            ]
