import asyncio
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode,tools_condition
from .node import *
from .state import ChatEPCISState
from .mcp_client import get_event_mcp_tools
from tool import *

class ChatEPCIS:
    def __init__(self,
            model_name:str,
            ollama_port:int=11434
        ):
        # tools
        # self.event_tool_list=[
        #     tool_get_len_epcis_event,
        #     tool_get_epcis_event_by_id,
        #     tool_get_epcis_event_by_event_type
        # ]
        self.event_tool_list=asyncio.run(get_event_mcp_tools())
        self.graph_tool_list=[
            tool_get_num_graph_elements,
            tool_get_node_degree
        ]

        self.agent_router_node=Agent_Router_Node(
            model_name=model_name,
            ollama_port=ollama_port
        )
        self.event_agent_node=Event_Agent_Node(
            model_name=model_name,
            ollama_port=ollama_port,
            tools=self.event_tool_list
        )
        self.graph_agent_node=Graph_Agent_Node(
            model_name=model_name,
            ollama_port=ollama_port,
            tools=self.graph_tool_list
        )
        self.final_answer_node=Final_Answer_Node(
            model_name=model_name,
            ollama_port=ollama_port
        )

    def get_agent(self):
        graph_builder=StateGraph(ChatEPCISState)

        ### Node
        graph_builder.add_node(
            "agent_router",
            self.agent_router_node.router
        )
        graph_builder.add_node(
            "agent_manager",
            self.agent_router_node.manager
        )
        graph_builder.add_node(
            "event_agent",
            self.event_agent_node.agent
        )
        graph_builder.add_node(
            "event_tools",
            ToolNode(self.event_tool_list)
        )
        graph_builder.add_node(
            "graph_agent",
            self.graph_agent_node.agent
        )
        graph_builder.add_node(
            "graph_tools",
            ToolNode(self.graph_tool_list)
        )
        graph_builder.add_node(
            "final_answer",
            self.final_answer_node.final_answer
        )

        ### Edge
        graph_builder.add_edge(
            START,
            "agent_router"
        )
        graph_builder.add_edge(
            "agent_router",
            "agent_manager"
        )
        graph_builder.add_conditional_edges(
            "agent_manager",
            self.agent_router_node.determinant,
            {
                "event_agent":"event_agent",
                "graph_agent":"graph_agent",
                "final_answer":"final_answer",
            }
        )
        graph_builder.add_conditional_edges(
            "event_agent",
            self.event_agent_node.router,
            {
                "event_tools":"event_tools",
                "agent_manager":"agent_manager"
            }
        )
        graph_builder.add_edge( # Tool 실행 후 다시 Event Agent
            "event_tools",
            "event_agent"
        )
        graph_builder.add_conditional_edges(
            "graph_agent",
            self.graph_agent_node.router,
            {
                "graph_tools":"graph_tools",
                "agent_manager":"agent_manager",
            }
        )
        graph_builder.add_edge( # Tool 실행 후 다시 graph Agent
            "graph_tools",
            "graph_agent"
        )
        graph_builder.add_edge(
            "final_answer",
            END
        )
        agent=graph_builder.compile()
        return agent






# class ChatEPCIS_old:
#     def __init__(self,
#             model_name:str,
#             port:int=11434
#         ):
#         mongoDB_tools=[
#             tool_get_epcis_event_by_id,
#             tool_get_epcis_event_by_event_type
#         ]
#         neo4j_tools=[
#             tool_get_num_graph_elements,
#             tool_get_node_degree
#         ]
#         self.tools=mongoDB_tools+neo4j_tools
#         self.agent_node=AgentNode(
#             model_name=model_name,
#             port=port,
#             tools=self.tools
#         )

#     def get_agent(self):
#         graph_builder=StateGraph(MessagesState)
#         graph_builder.add_node(
#             "llm_node",
#             self.agent_node.llm_node
#         )
#         graph_builder.add_node(
#             "tool_node",
#             ToolNode(self.tools)
#         )
#         graph_builder.add_edge(
#             START,
#             "llm_node",
#         )
#         graph_builder.add_conditional_edges(
#             "llm_node",
#             tools_condition,
#             {
#                 "tools":"tool_node",
#                 "__end__": END,
#             },
#         )
#         graph_builder.add_edge(
#             "tool_node",
#             "llm_node",
#         )
#         agent=graph_builder.compile()
#         return agent