import os
import argparse
import json
from module import MongoDB_Interface
from graph import OTG


"""
<< Test >> 
Check dataset
"""
def test_fn(**kwargs):
    match kwargs['test_num']:
        case 1:
            """
            Test. Check dataset
            """
            dataset_name=f"synthetic-food-supply-chain-dataset"
            dataset_path=os.path.join("..","data","epcis",dataset_name,f"{dataset_name}.json")
            with open(dataset_path,"r",encoding="utf-8") as f:
                data=json.load(f)

            ### data info
            print(f"keys of epcis document: {data.keys()}")
            epcis_body=data["epcisBody"]
            event_list=epcis_body["eventList"]
            print(f"length of event list: {len(event_list)}")
            event_type_count={
                "ObjectEvent":0,
                "AggregationEvent":0,
                "TransformationEvent":0,
                "TransactionEvent":0,
                "AssociationEvent":0,
            }
            for event in event_list:
                event_type_count[event["type"]]+=1
            print(event_type_count)
            print(event_list[0])

        case 2:
            """
            Test. Check OTG
            """
            mongodb_interface=MongoDB_Interface()
            graph=OTG()
        
            ### 1. get epcis events
            epcis_events=mongodb_interface.find_events()
        
            ### 2. convert to Object traceability graph
            graph_id=f"synthetic-food-supply-chain-dataset"
            graph_elements=graph.transform_epcis_events_to_graph(events=epcis_events,graph_id=graph_id)
            nodes=graph_elements["nodes"]
            edge_events=graph_elements["edge_events"]
            print(f"length of nodes: {len(nodes)}")
            print(f"length of edge events: {len(edge_events)}")

if __name__=="__main__":
    """
    Execute test_fn
    """
    parser=argparse.ArgumentParser()
    parser.add_argument("--test_num",type=int,default=1)
    args=parser.parse_args()
    test_config={
        "test_num":args.test_num
    }
    test_fn(**test_config)