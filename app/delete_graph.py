import argparse
from module import Neo4j_Interface

"""
<< App >>
"""
def app(**kwargs):
    """
    """
    neo4j_interface=Neo4j_Interface()
    graph_id=kwargs["graph_id"]
    neo4j_interface.delete_specific_graph(graph_id=graph_id)

if __name__=="__main__":
    """
    Execute app
    """
    parser=argparse.ArgumentParser()
    parser.add_argument("--graph_id",type=str,default=f"supply_chain") # supply_chain, test_graph
    args=parser.parse_args()
    app_config={
        "graph_id":args.graph_id
    }
    app(**app_config)