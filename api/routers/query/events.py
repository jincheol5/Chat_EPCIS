from fastapi import APIRouter,Request,status
from starlette.concurrency import run_in_threadpool
from module import CaptureModule,MongoDB_Interface
from schema.epcis_document import EPCISEventType
from .response import event_query_document,require_events

query_events_router=APIRouter(prefix="/events",tags=["events"])

@query_events_router.get("/")
async def get_all_events(request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events)
    return event_query_document(events)

@query_events_router.post("/",status_code=status.HTTP_201_CREATED)
async def capture_event(event:EPCISEventType,request:Request):
    db:MongoDB_Interface=request.app.state.db
    transformed_event=CaptureModule.transform_events(event_list=[event])[0]
    await run_in_threadpool(
        db.insert_data_list,
        data_list=[transformed_event],
        data_type="event"
    )
    transformed_event.pop("_id",None)
    return transformed_event

@query_events_router.get("/{eventID}")
async def get_event_of_eventID(eventID:str,request:Request):
    db:MongoDB_Interface=request.app.state.db
    events=await run_in_threadpool(db.find_events_by_event_id,eventID)
    return event_query_document(require_events(events))
