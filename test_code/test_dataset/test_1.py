import os
import argparse
import json

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