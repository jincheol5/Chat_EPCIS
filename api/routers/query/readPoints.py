from fastapi import APIRouter,Request
from starlette.concurrency import run_in_threadpool
from module import MongoDB_Interface
from .response import event_query_document,event_subresource,require_events,uri_collection

query_readPoints_router=APIRouter(prefix="/readPoints",tags=["readPoints"])

@query_readPoints_router.get("/")
async def get_readPoints(request:Request):
    db:MongoDB_Interface=request.app.state.db
    values=await run_in_threadpool(db.find_read_points)
    return uri_collection(values)

@query_readPoints_router.get("/{readPoint}")
async def get_resources_of_readPoint(readPoint:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_read_point,readPoint)
    return event_subresource(request,bool(events))

@query_readPoints_router.get("/{readPoint}/events")
async def get_events_of_readPoint(readPoint:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_read_point,readPoint)
    return event_query_document(require_events(events))
