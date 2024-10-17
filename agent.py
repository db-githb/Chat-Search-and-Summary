from typing import Annotated, List
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph.message import AnyMessage, add_messages


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class Assistant:
    def __init__(self, llm, tools):
        """
        Initialize the Assistant with a runnable object.

        Args:
            runnable (Runnable): The runnable instance to invoke.
        """
        # Create the primary assistant prompt template
        self.primary_assistant_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant tasked with answering user questions."
                    "You have access to two tools: chat_summary and web_search."
                    "You use each tool once only."
                    "First, use chat_summary to see if it has any relevant information that could answer the question.  Be very precise when you query chat_summary."
                    "Second, for any questions about current events, use the web_search tool to get information from the web."
                    "If you don't know the answer, just say that you don't know."
                ),
                ("placeholder", "{messages}"),
            ]
        )

        self.runnable = self.primary_assistant_prompt | llm.bind_tools(tools)

    def __call__(self, state: State, config: RunnableConfig):
        """
        Call method to invoke the LLM and handle its responses.
        Re-prompt the assistant if the response is not a tool call or meaningful text.

        Args:
            state (State): The current state containing messages.
            config (RunnableConfig): The configuration for the runnable.

        Returns:
            dict: The final statte containing the updated messages
        """
        while True:
            result = self.runnable.invoke(state) #Invoke the LLM
            if not result.tool_calls and(
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}