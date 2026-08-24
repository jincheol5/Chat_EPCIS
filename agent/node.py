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

    def agent_manager_node(self,
            state:ChatEPCISState
        ):
        agent_queue=state["agent_queue"]
        if not agent_queue:
            return {
                "current_agent":None
            }
        return {
            "current_agent":agent_queue[0],
            "agent_queue":agent_queue[1:]
        }

    def agent_decision_node(self,
            state:ChatEPCISState
        ):
        """
        Agent Manager가 선택한 current_agent에 따라 다음 Agent Node 결정
        """
        current_agent=state["current_agent"]
        if current_agent is None:
            return "final_answer"
        return current_agent

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

    def route_event_agent(self,
            state:ChatEPCISState
        ):
        last_message=state["messages"][-1]
        if last_message.tool_calls:
            return "event_tools"
        return "agent_manager"

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

    def route_graph_agent(self,
            state:ChatEPCISState
        ):
        last_message=state["messages"][-1]
        if last_message.tool_calls:
            return "graph_tools"
        return "agent_manager"

class Basic_Agent_Node:
    def __init__(
            self,
            model_name:str="gemma4",
            port:int=11434
        ):
        self.llm=ChatOllama(
            model=model_name,
            base_url=f"http://127.0.0.1:{port}",
            temperature=0,
        )

    def basic_agent_node(
            self,
            state:ChatEPCISState
        ):
        response=self.llm.invoke([
            SystemMessage(
                content=Prompt.BASIC_AGENT_SYSTEM_PROMPT
            ),
            *state["messages"]
        ])
        return {
            "messages": [response]
        }

class Final_Answer_Node:
    def __init__(
            self,
            model_name:str="gemma4",
            port:int=11434
        ):
        self.llm=ChatOllama(
            model=model_name,
            base_url=f"http://127.0.0.1:{port}",
            temperature=0,
        )

    def final_answer_node(
            self,
            state:ChatEPCISState
        ):
        response=self.llm.invoke([
            SystemMessage(
                content=Prompt.FINAL_ANSWER_SYSTEM_PROMPT
            ),
            *state["messages"]
        ])

        return {
            "messages": [response]
        }



