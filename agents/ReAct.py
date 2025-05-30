import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage # The foundational class for all message types in LangGraph.
from langchain_core.messages import ToolMessage # passes data back to LLM after it calls a tool such as the content and tool_call_id'
from langchain_core.messages import SystemMessage # message for providing instructions to the LLM
from langchain_openai import ChatOpenAI  # OpenAI's chat model for generating responses
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()


# Annotated provides additional context without affecting the type itself.
# Sequence - To automatically handle the state updates for sequences such as by adding new messages to a chat hitory.

# add_message is reducer function
# Reducer function.
# Rule that controls how updates from nodes are combined with the existing state.
# Tells us how to merge new data into the current state.

# Without a reduces, updates would have replaced the existing value entirely.

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def add_numbers(a: int, b: int) -> int:
    """This is an addition function that Adds two numbers together."""
    return a + b

@tool
def subtract(a: int, b:int):
    """subtraction function"""
    return a-b

@tool
def multiply(a: int, b: int):
    """Multiplication function"""
    return a*b

tools = [add_numbers, multiply, subtract]

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

llm = ChatOpenAI(model=model, base_url=endpoint, api_key=token).bind_tools(tools)

def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=
        "You are my AI assistant, please answer my query to the best of your ability"
    )
    response = llm.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"
    
graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    }
)

graph.add_edge("tools", "our_agent")
app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs1 = {"messages": [("user", "Add 3 + 4. Add 27 + 34")]}
print_stream(app.stream(inputs1, stream_mode="values"))

inputs2 = {"messages": [("user", "Add 40 + 12 and then multiply the result by 6. Also tell me a good joke")]}
print_stream(app.stream(inputs2, stream_mode="values"))
