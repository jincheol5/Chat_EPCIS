from typing import Literal,Any
from module import MongoDB_Interface
from langchain.tools import tool

mongoDB_interface=MongoDB_Interface()

@tool
def tool_get_len_epcis_event()->int:
    """
    MongoDB에 저장된 모든 EPCIS event 개수를 조회합니다.

    Return:
        int: MongoDB에 저장된 EPCIS event 개수
    """
    return len(mongoDB_interface.find_events())

@tool
def tool_get_epcis_event_by_id(
        event_id:str
    )->dict[str,Any]|None:
    """
    MongoDB에 저장된 EPCIS event를 event_id로 조회합니다.

    Return: dict[str,Any] | None
        event_id와 일치하는 EPCIS event가 존재하면 해당 event를 Python dictonary 형태로 반환합니다. 
        일치하는 event가 없으면 None을 반환합니다. 

        반환 예시: 
            { 
                "_id": "event-001", 
                "type": "ObjectEvent", 
                "eventTime": "2024-01-01T11:30:46+00:00", 
                "action": "ADD", 
                "bizStep": "shipping" 
            }
    """
    return mongoDB_interface.find_event_by_id(event_id=event_id)

@tool
def tool_get_epcis_event_by_event_type(
        event_type:Literal[
            "ObjectEvent",
            "AggregationEvent",
            "TransformationEvent",
            "TransactionEvent",
            "AssociationEvent"
        ],
        limit:int=1
    )->list[dict[str,Any]]|None:
    """
    MongoDB에 저장된 EPCIS event를 event_type으로 조회합니다.

    Return: list[dict[str,Any] | None
        event_type과 일치하는 최대 limit개의 EPCIS event list
    """
    return mongoDB_interface.find_events_by_event_type(event_type=event_type,limit=limit)