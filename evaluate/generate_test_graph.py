from module import MongoDB_Interface,Neo4j_Interface
from graph import OTG

def convert_to_graph():
    """
    """
    mongodb_interface=MongoDB_Interface(isEvaluated=True)
    neo4j_interface=Neo4j_Interface()
    graph=OTG()

    ### 1. get epcis events
    epcis_events=mongodb_interface.find_events()

    ### 2. convert to Object traceability graph
    graph_id=f"test_graph"
    graph_elements=graph.transform_epcis_events_to_graph(events=epcis_events,graph_id=graph_id)
    nodes=graph_elements["nodes"]
    edge_events=graph_elements["edge_events"]

    ### 3. save in Neo4j
    neo4j_interface.add_nodes(graph_id=graph_id,nodes=nodes)
    neo4j_interface.add_edge_events(graph_id=graph_id,edge_events=edge_events)

if __name__=="__main__":
    convert_to_graph()
