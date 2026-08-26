from typing import Any,Literal

from fastmcp import FastMCP

from module import MongoDB_Interface


mcp=FastMCP("Chat EPCIS Event Server")
mongoDB_interface=MongoDB_Interface()


@mcp.tool
def tool_get_len_epcis_event()->int:
	"""
	MongoDB에 저장된 모든 EPCIS event 개수를 조회합니다.
	"""
	return len(mongoDB_interface.find_events())


@mcp.tool
def tool_get_epcis_event_by_id(
		event_id:str
	)->dict[str,Any]|None:
	"""
	MongoDB에 저장된 EPCIS event를 event_id로 조회합니다.
	"""
	return mongoDB_interface.find_event_by_id(event_id=event_id)


@mcp.tool
def tool_get_epcis_event_by_event_type(
		event_type:Literal[
			"ObjectEvent",
			"AggregationEvent",
			"TransformationEvent",
			"TransactionEvent",
			"AssociationEvent"
		],
		limit:int=1
	)->list[dict[str,Any]]:
	"""
	MongoDB에 저장된 EPCIS event를 event_type으로 조회합니다.
	"""
	return mongoDB_interface.find_events_by_event_type(
		event_type=event_type,
		limit=limit,
	)


if __name__=="__main__":
	mcp.run()
