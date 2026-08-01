from module import MongoDB_Interface,Neo4j_Interface
from graph import OTG

"""
<< App >>
"""
def app():
    """
    """
    mongodb_interface=MongoDB_Interface()
    neo4j_interface=Neo4j_Interface()
    graph=OTG()

    ### 1. get epcis events
    epcis_events=mongodb_interface.find_events()

    ### 2. convert to Object traceability graph
    graph_elements=graph.transform_epcis_events_to_graph(events=epcis_events)
    nodes=graph_elements["nodes"]
    edge_events=graph_elements["edge_events"]

    ### 3. save in Neo4j
    neo4j_interface.add_nodes(nodes=nodes)
    neo4j_interface.add_edge_events(edge_events=edge_events)

if __name__=="__main__":
    """
    Execute app
    """
    app()