from fastapi import APIRouter,Request
from starlette.concurrency import run_in_threadpool
from module import MongoDB_Interface
from .response import event_query_document,event_subresource,require_events,uri_collection

query_epcs_router=APIRouter(prefix="/epcs",tags=["epcs"])

@query_epcs_router.get("/")
async def get_epcs(request:Request):
    db:MongoDB_Interface=request.app.state.db
    values=await run_in_threadpool(db.find_epcs)
    return uri_collection(values)

@query_epcs_router.get("/{epc}")
async def get_resources_of_epc(epc:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_epc,epc)
    return event_subresource(request,bool(events))

@query_epcs_router.get("/{epc}/events")
async def get_events_of_epc(epc:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_epc,epc)
    return event_query_document(require_events(events))
