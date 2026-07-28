from fastapi import APIRouter,Request
from starlette.concurrency import run_in_threadpool
from module import MongoDB_Interface
from .response import event_query_document,event_subresource,require_events,uri_collection

query_bizSteps_router=APIRouter(prefix="/bizSteps",tags=["bizSteps"])

@query_bizSteps_router.get("/")
async def get_bizSteps(request:Request):
    db:MongoDB_Interface=request.app.state.db
    values=await run_in_threadpool(db.find_biz_steps)
    return uri_collection(values)

@query_bizSteps_router.get("/{bizStep}")
async def get_resources_of_bizStep(bizStep:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_biz_step,bizStep)
    return event_subresource(request,bool(events))

@query_bizSteps_router.get("/{bizStep}/events")
async def get_events_of_bizStep(bizStep:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_biz_step,bizStep)
    return event_query_document(require_events(events))
