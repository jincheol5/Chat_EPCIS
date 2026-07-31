import os
import argparse
import json
import requests

"""
<< App >>
"""
def app(**kwargs):
    """
    """
    dataset_name=kwargs["dataset_name"]
    dataset_path=os.path.join("..","data","epcis",dataset_name,f"{dataset_name}.json")
    with open(dataset_path,"r",encoding="utf-8") as f:
        data=json.load(f)
    url=f"http://127.0.0.1:{kwargs['port']}{kwargs['end_point']}/"
    try:
        response=requests.post(
            url=url,
            json=data,
            timeout=60,
        )
        response.raise_for_status()
        print(f"Capture 성공: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Capture 실패: {e}")

if __name__=="__main__":
    """
    Execute app
    """
    parser=argparse.ArgumentParser()
    parser.add_argument("--dataset_name",type=str,default=f"synthetic-food-supply-chain-dataset")
    parser.add_argument("--end_point",type=str,default=f"/capture")
    parser.add_argument("--port",type=int,default=8000)
    args=parser.parse_args()
    app_config={
        "dataset_name":args.dataset_name,
        "end_point":args.end_point,
        "port":args.port
    }
    app(**app_config)