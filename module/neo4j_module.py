import networkx as nx
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

    def insert_graph(self,graph:nx.MultiDiGraph):
        """
        """