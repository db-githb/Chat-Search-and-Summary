import streamlit as st
from tools import Tools
from agent import Assistant
from graph import Graph, Graph2
from langchain_ollama import ChatOllama
import uuid
from langchain_core.messages import HumanMessage, AIMessage

# Set app layout
title = "Chat Search-and-Summary"
st.set_page_config(page_title=title, page_icon= ":material/chat:")
st.title(title)

# Load LLM
llm = ChatOllama(model="llama3.2:3b-instruct-fp16", temperature=0)
tools = Tools()
tools_lst = [tools.chat_summary, tools.web_search]
agent = Assistant(llm, tools_lst)
graph_obj = Graph(agent, tools_lst)
#llm_with_tools = llm.bind_tools(tools_lst)
#graph_obj = Graph2(llm_with_tools, tools_lst)
graph = graph_obj.get_graph()
config = {"configurable": {"thread_id": str(uuid.uuid4())}}

# Initialize chat history - session_state is an object that keeps all the variables persistent throughout the streamlit session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Show Conversation
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human",  avatar=":material/person:"):
            st.markdown(message.content)
    else:
        with st.chat_message("AI", avatar=":material/computer:"):
            st.markdown(message.content)

# User input (intialize chat widget with "Enter Query")
user_query = st.chat_input("Enter query")
    #if user_query.lower() in ["quit", "exit", "q"]:
    #    st.markdown("Goodbye!")
    #    break
    
if user_query is not None and user_query != "":

    for event in graph.stream({"messages": ("user", user_query)}, config, stream_mode="values"):
        # print(event) - use for debugging
        response = event["messages"][-1].content
        msg_typ = event["messages"][-1].type

        if msg_typ == "human":
            # Append user message to chat history with langchain's message schema
            st.session_state.chat_history.append(HumanMessage(user_query))
            tools.state_history = (st.session_state.chat_history)
            # Show user message in the application
            with st.chat_message("Human", avatar=":material/person:"):
                st.markdown(event["messages"][-1].content)

        if msg_typ == "ai" and response != "":
                # Append ai response into chat history with langchain's message schema
                st.session_state.chat_history.append(AIMessage(response))
                tools.state_history = (st.session_state.chat_history)
                # Show AI message in the application
                with st.chat_message("AI", avatar=":material/computer:"):
                    st.markdown(event["messages"][-1].content)