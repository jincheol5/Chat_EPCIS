from langgraph.graph import StateGraph,START,END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode,tools_condition
from .node import AgentNode
from tool import *

class ChatEPCIS:
    def __init__(self,
            model_name:str,
            port:int=11434
        ):
        mongoDB_tools=[
            tool_get_epcis_event_by_id,
            tool_get_epcis_event_by_event_type
        ]
        neo4j_tools=[
            tool_get_num_graph_elements,
            tool_get_node_degree
        ]
        self.tools=mongoDB_tools+neo4j_tools
        self.agent_node=AgentNode(
            model_name=model_name,
            port=port,
            tools=self.tools
        )

    def get_agent(self):
        graph_builder=StateGraph(MessagesState)
        graph_builder.add_node(
            "llm_node",
            self.agent_node.llm_node
        )
        graph_builder.add_node(
            "tool_node",
            ToolNode(self.tools)
        )
        graph_builder.add_edge(
            START,
            "llm_node",
        )
        graph_builder.add_conditional_edges(
            "llm_node",
            tools_condition,
            {
                "tools":"tool_node",
                "__end__": END,
            },
        )
        graph_builder.add_edge(
            "tool_node",
            "llm_node",
        )
        agent=graph_builder.compile()
        return agent