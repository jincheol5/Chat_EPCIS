from typing import Literal,Any
from module import MongoDB_Interface
from langchain.tools import tool

mongoDB_interface=MongoDB_Interface()

@tool
def tool_len_event(
        event_type:Literal[
            "ObjectEvent",
            "AggregationEvent",
            "TransformationEvent",
            "TransactionEvent",
            "AssociationEvent"
        ]|None=None
    )->int:
    """
    MongoDB event database에 저장된 모든 event 개수를 조회합니다.
    event_type 값이 None이 아닌 경우, 해당 event type의 event 개수를 조회합니다.

    Input:
        event_type: EPCIS Event type, default = None 
    Return:
        int: MongoDB에 저장된 event 개수
    """
    mongoDB_interface.set_collection(collection_name="event")
    if event_type is not None:
        query={
            "event_type":event_type
        }
        return len(mongoDB_interface.find_events(query=query))
    else:
        return len(mongoDB_interface.find_events())

@tool
def tool_(

    ):
    """
    
    """

