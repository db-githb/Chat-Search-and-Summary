
<h1> <p style="text-align:center;"> Chat Search-and-Summary <p> </h1>

Chat-GPT clone using LangGraph to implement a Retrieval Augmented Generation (RAG) agent, equipped with web search and document summary tools, wrapped in a Streamlit GUI.

Tools available to RAG Agent:
- Web search
- Chat history
- PDF document summary (coming)

## Requirements
Language: Python 3.10
Models: llama3.2:3b-instruct-fp16, llama3.1

## Setup
```
py -m venv \path\to\venv

\path\to\venv\Scripts\activate.bat

pip install -r requirements.txt
```

## Run
```\path\to\project> streamlit run main.py```

## Notes to self
- Chat history tool is currently another llm that is queried by the RAG agent with vector embeddings of the chat history as context  
(1) Creating vector embeddings with every query is very slow\
(2) This llm should at least be another agent and not a tool
    - or figure out how to have chat history persist outside of streamlit

<img src="chat-search-and-summary.png" 
        alt="Picture" 
        width="380" 
        height="401" 
        style="display: block; margin: 0 auto" />
