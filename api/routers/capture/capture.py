from fastapi import APIRouter,Request,HTTPException
from starlette.concurrency import run_in_threadpool
from schema import EPCISDocument
from module import CaptureModule,MongoDB_Interface

capture_router=APIRouter(prefix="/capture",tags=["capture"])

@capture_router.post("/")
async def capture(document:EPCISDocument,request:Request):
    db:MongoDB_Interface=request.app.state.db
    try:
        event_list,vocabulary_list=CaptureModule.extract_from_epcis_document(document=document)
        event_list=CaptureModule.transform_events(event_list=event_list)
        vocab_element_list=CaptureModule.transform_vocabularies(vocabulary_list=vocabulary_list)
        if event_list:
            await run_in_threadpool(
                db.insert_data_list,
                data_list=event_list,
                data_type="event"
            )
        if vocab_element_list:
            await run_in_threadpool(
                db.insert_data_list,
                data_list=vocab_element_list,
                data_type="vocab"
            )
        return {"message":"EPCIS document captured successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to capture EPCIS document: {str(e)}"
        )
