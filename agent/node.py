from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from .prompt import Prompt
from .schema import RouterOutput
from .state import ChatEPCISState

class Agent_Router_Node:
    def __init__(self,
            model_name:str=f"gemma4",
            port:int=11434
        ):
        self.llm=ChatOllama(
            model=model_name,
            base_url=f"http://127.0.0.1:{port}",
            temperature=0,
        )
        self.llm.with_structured_output(schema=RouterOutput)

    def agent_router_node(self,
            state:ChatEPCISState
        ):
        response=self.llm.invoke([
            SystemMessage(content=Prompt.ROUTER_SYSTEM_PROMPT),
            *state["messages"]
        ])
        return {
            "agent_queue":response.agents
        }

    def select_agent_node(self,
            state:ChatEPCISState
        ):
        """
        """

class Event_Agent_Node:
    def __init__(self,
            model_name:str=f"gemma4",
            port:int=11434,
            tools:list=[]
        ):
        self.llm=ChatOllama(
            model=model_name,
            base_url=f"http://127.0.0.1:{port}",
            temperature=0,
        )
        self.llm=self.llm.bind_tools(tools)

    def event_agent_node(self,
            state:ChatEPCISState
        ):
        response=self.llm.invoke([
            SystemMessage(content=Prompt.EVENT_AGENT_SYSTEM_PROMPT),
            *state["messages"]
        ])
        return {
            "messages":[response]
        }

    def event_agent_router(self,
            state:ChatEPCISState
        ):
        last_message=state["messages"][-1]

class Graph_Agent_Node:
    def __init__(self,
            model_name:str=f"gemma4",
            port:int=11434,
            tools:list=[]
        ):
        self.llm=ChatOllama(
            model=model_name,
            base_url=f"http://127.0.0.1:{port}",
            temperature=0,
        )
        self.llm=self.llm.bind_tools(tools)

    def graph_agent_node(self,
            state:ChatEPCISState
        ):
        response=self.llm.invoke(
            [
                SystemMessage(content=Prompt.GRAPH_AGENT_SYSTEM_PROMPT),
                *state["messages"],
            ]
        )
        return {
            "messages":[response]
        }

    def graph_agent_router(self,
            state:ChatEPCISState
        ):
        last_message=state["messages"][-1]