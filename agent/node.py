from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from .prompt import Prompt
from .schema import RouterOutput
from .state import ChatEPCISState

class Agent_Router_Node:
    def __init__(self,
            model_name:str=f"gemma4:e4b",
            ollama_port:int=11434
        ):
        self.llm=ChatOllama(
            model=model_name,
            base_url=f"http://127.0.0.1:{ollama_port}",
            temperature=0,
        )
        self.llm=self.llm.with_structured_output(schema=RouterOutput)

    def router(self,
            state:ChatEPCISState
        ):
        response=self.llm.invoke([
            SystemMessage(content=Prompt.ROUTER_SYSTEM_PROMPT),
            *state["messages"]
        ])
        return {
            "agent_queue":response.agents
        }

    def manager(self,
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

    def determinant(self,
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
            ollama_port:int=11434,
            tools:list=[]
        ):
        self.llm=ChatOllama(
            model=model_name,
            base_url=f"http://127.0.0.1:{ollama_port}",
            temperature=0,
        )
        self.llm=self.llm.bind_tools(tools)

    def router(self,
            state:ChatEPCISState
        ):
        last_message=state["messages"][-1]
        if last_message.tool_calls:
            return "event_tools"
        return "agent_manager"

    def agent(self,
            state:ChatEPCISState
        ):
        response=self.llm.invoke([
            SystemMessage(content=Prompt.EVENT_AGENT_SYSTEM_PROMPT),
            *state["messages"]
        ])
        return {
            "messages":[response]
        }

class Graph_Agent_Node:
    def __init__(self,
            model_name:str=f"gemma4",
            ollama_port:int=11434,
            tools:list=[]
        ):
        self.llm=ChatOllama(
            model=model_name,
            base_url=f"http://127.0.0.1:{ollama_port}",
            temperature=0,
        )
        self.llm=self.llm.bind_tools(tools)

    def router(self,
            state:ChatEPCISState
        ):
        last_message=state["messages"][-1]
        if last_message.tool_calls:
            return "graph_tools"
        return "agent_manager"

    def agent(self,
            state:ChatEPCISState
        ):
        response=self.llm.invoke([
            SystemMessage(content=Prompt.GRAPH_AGENT_SYSTEM_PROMPT),
            *state["messages"],
        ])
        return {
            "messages":[response]
        }

class Final_Answer_Node:
    def __init__(
            self,
            model_name:str="gemma4",
            ollama_port:int=11434
        ):
        self.llm=ChatOllama(
            model=model_name,
            base_url=f"http://127.0.0.1:{ollama_port}",
            temperature=0,
        )

    def final_answer(
            self,
            state:ChatEPCISState
        ):
        response=self.llm.invoke([
            SystemMessage(content=Prompt.FINAL_ANSWER_SYSTEM_PROMPT),
            *state["messages"]
        ])
        return {
            "messages": [response]
        }



