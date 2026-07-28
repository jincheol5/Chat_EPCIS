from fastapi import APIRouter,Request
from starlette.concurrency import run_in_threadpool
from module import MongoDB_Interface
from .response import event_query_document,event_subresource,require_events,uri_collection

query_eventTypes_router=APIRouter(prefix="/eventTypes",tags=["eventTypes"])

@query_eventTypes_router.get("/")
async def get_eventTypes(request:Request):
    db:MongoDB_Interface=request.app.state.db
    event_types=await run_in_threadpool(db.find_event_types)
    return uri_collection(event_types)

@query_eventTypes_router.get("/{eventType}")
async def get_resources_of_eventType(eventType:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_event_type,eventType)
    return event_subresource(request,bool(events))

@query_eventTypes_router.get("/{eventType}/events")
async def get_events_of_eventType(eventType:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_event_type,eventType)
    return event_query_document(require_events(events))
