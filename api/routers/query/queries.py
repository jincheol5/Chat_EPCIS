from fastapi import APIRouter,Request
from module import MongoDB_Interface

queries_router=APIRouter(prefix="/queries",tags=["queries"])
"""
Named Query 관련
"""

@queries_router.get("/")
def get_queries(request:Request):
    db:MongoDB_Interface=request.app.state.db

@queries_router.post("/")
def create_query(request:Request):
    db:MongoDB_Interface=request.app.state.db

@queries_router.get("/{queryName}")
def get_query(
        queryName:str,
        request:Request
    ):
    db:MongoDB_Interface=request.app.state.db

@queries_router.post("/{queryName}")
def create_and_execute_query(
        queryName:str,
        request:Request
    ):
    db:MongoDB_Interface=request.app.state.db

@queries_router.delete("/{queryName}")
def delete_query(
        queryName:str,
        request:Request
    ):
    db:MongoDB_Interface=request.app.state.db

@queries_router.get("/{queryName}/events")
def get_events_of_query(
        queryName:str,
        request:Request
    ):
    db:MongoDB_Interface=request.app.state.db

@queries_router.get("/{queryName}/subscriptions")
def get_subscriptions_of_query(
        queryName:str,
        request:Request
    ):
    db:MongoDB_Interface=request.app.state.db

@queries_router.post("/{queryName}/subscriptions")
def create_subscription_of_query(
        queryName:str,
        request:Request
    ):
    db:MongoDB_Interface=request.app.state.db

@queries_router.get("/{queryName}/subscriptions/{subscriptionID}")
def get_subscription_of_query(
        queryName:str,
        subscriptionID:str,
        request:Request
    ):
    db:MongoDB_Interface=request.app.state.db

@queries_router.delete("/{queryName}/subscriptions/{subscriptionID}")
def delete_subscription_of_query(
        queryName:str,
        subscriptionID:str,
        request:Request
    ):
    db:MongoDB_Interface=request.app.state.db
