import os
import toml
from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

class Tools:
    def __init__(self):
        secrets = toml.load("./secrets.toml")
        os.environ["TAVILY_API_KEY"] = secrets["TAVILY_API_KEY"]
        self.web_search_tool = TavilySearchResults()
        self.model = "llama3.1"
        self.embeddings = OllamaEmbeddings(model=self.model,)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        self.llm = ChatOllama(model=self.model, temperature=0)
        self.state_history = {}
        self.prompt = ChatPromptTemplate.from_messages(
                  [
                    ("system", "You are a knowledgeable AI assistant. Summarize {context} and use it to answer the user questions."),
                    ("user", "{question}"),
                   ]
                )
        
    def format_docs(self,docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    def get_chat_history(self):
        chat_history = ""
        for message in self.state_history:
            if isinstance(message, HumanMessage):
                chat_history += "User: "+message.content+" "
            #else:
            #    chat_history += "Assistant: "+message.content+" "
        return chat_history

    def chat_summary(self,query: str) -> str:
        """run chat summary to answer question"""
        llm = self.llm
        chat_history = self.get_chat_history()


        docs = [Document(page_content=x) for x in self.text_splitter.split_text(chat_history)]

        # Split - split docs into chunk size of 500 characters
        all_splits = self.text_splitter.split_documents(docs)

        # Embed - every split is embedded and indexed into this local vector store 
        vectorstore = FAISS.from_documents(documents=all_splits, embedding=self.embeddings)
        
        qa_chain = (
            {
                "context": vectorstore.as_retriever() | self.format_docs,
                "question": RunnablePassthrough(),
            }
            | self.prompt
            | llm
            | StrOutputParser()
        )
        summary = qa_chain.invoke(query)
        return Document(page_content=summary) 

    def web_search(self,query: str) -> str:
        """run web search on the question."""
        web_results = self.web_search_tool.invoke({"query": query})
        return [
            Document(page_content=d["content"], metadata={"url": d["url"]}) for d in web_results
        ]