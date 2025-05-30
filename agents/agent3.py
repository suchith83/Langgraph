import os
import requests
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import datetime
import json

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add_numbers(a: int, b: int) -> int:
    """This is an addition function that Adds two numbers together."""
    return a + b

tools = [add_numbers]

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference/v1/chat/completions"
model = "openai/gpt-4.1"

def model_call(state: AgentState) -> AgentState:
    system_message = SystemMessage(content="You are my AI assistant, please answer my query to the best of your ability")
    messages = [system_message] + state["messages"]
    
    payload = {
        "model": model,
        "messages": [{"role": msg.type, "content": msg.content} for msg in messages],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.args,
                        "required": list(tool.args.keys())
                    },
                }
            } for tool in tools
        ],
        "tool_choice": "auto",
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(endpoint, headers=headers, json=payload)
    result = response.json()

    # Log Rate Limit Headers
    print("\n📊 Rate Limit Info:")
    print("X-RateLimit-Limit:", response.headers.get("X-RateLimit-Limit"))
    print("X-RateLimit-Remaining:", response.headers.get("X-RateLimit-Remaining"))
    reset = response.headers.get("X-RateLimit-Reset")
    if reset:
        reset_time = datetime.datetime.fromtimestamp(int(reset))
        print("X-RateLimit-Reset:", reset_time)

    reply = result["choices"][0]["message"]
    return {"messages": [AIMessage(content=reply["content"])]}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and getattr(last_message, "tool_calls", None):
        return "continue"
    return "end"

graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")
graph.add_conditional_edges("our_agent", should_continue, {
    "continue": "tools",
    "end": END,
})
graph.add_edge("tools", "our_agent")

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            print(f"💬 {message.content}")

inputs = {"messages": [HumanMessage(content="Add 37 + 26.")]}
print_stream(app.stream(inputs, stream_mode="values"))
