from fastapi import APIRouter,Request
from starlette.concurrency import run_in_threadpool
from module import MongoDB_Interface
from .response import event_query_document,event_subresource,require_events,uri_collection

query_dispositions_router=APIRouter(prefix="/dispositions",tags=["dispositions"])

@query_dispositions_router.get("/")
async def get_dispositions(request:Request):
    db:MongoDB_Interface=request.app.state.db
    values=await run_in_threadpool(db.find_dispositions)
    return uri_collection(values)

@query_dispositions_router.get("/{disposition}")
async def get_resources_of_disposition(disposition:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_disposition,disposition)
    return event_subresource(request,bool(events))

@query_dispositions_router.get("/{disposition}/events")
async def get_events_of_disposition(disposition:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_disposition,disposition)
    return event_query_document(require_events(events))
