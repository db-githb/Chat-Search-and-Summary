from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from IPython.display import Image, display
from agent import Assistant, State
from utils import  create_tool_node_with_fallback

from typing_extensions import TypedDict
from typing import Annotated, List
from langgraph.graph.message import AnyMessage, add_messages


class Graph:
    def __init__(self, agent, tools):
        # Graph
        self.builder = StateGraph(State)

        # Define nodes: these do the work
        self.builder.add_node("assistant", agent)
        self.builder.add_node("tools", create_tool_node_with_fallback(tools))

        # Define edges: these determine how the control flow move
        self.builder.add_edge(START, "assistant")
        self.builder.add_conditional_edges(
            "assistant",
            # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
            # If the latest message (result from assistant is a not a tool call -> tools_condition routes to END)
            tools_condition,
            )
        self.builder.add_edge("tools", "assistant")
        # self.memory = SqliteSaver.from_conn_string(":memory:")
        self.memory = MemorySaver()
        self.graph = self.builder.compile(checkpointer=self.memory) # The checkpointer lets the graph persist its state

    def get_graph(self):
        
        return self.graph

# Alternate Graph Structure
class Graph2:
    def __init__(self, agent, tools):
        self.builder = StateGraph(State)
        self.llm = agent
         # Define nodes: these do the work
        self.builder.add_node("assistant", self.chatbot)
        tool_node = ToolNode(tools=tools)
        self.builder.add_node("tools", tool_node)

        # Define edges: these determine how the control flow move
        self.builder.add_edge(START, "assistant")
        self.builder.add_conditional_edges(
            "assistant",
            tools_condition,
            )
        self.builder.add_edge("tools", "assistant")
        # self.memory = SqliteSaver.from_conn_string(":memory:")
        self.memory = MemorySaver()
        self.graph = self.builder.compile(checkpointer=self.memory) # The checkpointer lets the graph persist its state
    
    def get_graph(self):
        return self.graph
    
    def chatbot(self,state: State):
     return {"messages": [self.llm.invoke(state["messages"])]}