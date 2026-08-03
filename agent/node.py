from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from .state import AgentState
from .prompt import Prompt

class AgentNode:
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

    def llm_node(self,
            state:AgentState
        ):
        response=self.llm.invoke(
            [
                SystemMessage(content=Prompt.SYSTEM_PROMPT),
                *state["messages"],
            ]
        )
        return {
            "messages":[response]
        }