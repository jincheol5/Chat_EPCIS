import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from module import MongoDB_Interface
from api.routers.capture.capture import capture_router
from api.routers.query.queries import queries_router 
from api.routers.query.events import query_events_router
from api.routers.query.eventTypes import query_eventTypes_router
from api.routers.query.epcs import query_epcs_router
from api.routers.query.bizSteps import query_bizSteps_router
from api.routers.query.bizLocations import query_bizLocations_router
from api.routers.query.readPoints import query_readPoints_router
from api.routers.query.dispositions import query_dispositions_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    app.state.db=MongoDB_Interface() # 서버 시작 시 1번 생성
    yield # 이 줄을 기준으로 위쪽은 서버 시작 시 실행되는 코드, 아래쪽은 서버 종료 시 실행되는 코드
    app.state.db.disconnect_db() # 서버 종료 시 1번 종료

app=FastAPI(lifespan=lifespan)
app.include_router(capture_router)
app.include_router(queries_router)
app.include_router(query_events_router)
app.include_router(query_eventTypes_router)
app.include_router(query_epcs_router)
app.include_router(query_bizSteps_router)
app.include_router(query_bizLocations_router)
app.include_router(query_readPoints_router)
app.include_router(query_dispositions_router)

if __name__ == "__main__":
    uvicorn.run("api.main:app",host="127.0.0.1",port=8000,reload=True)
