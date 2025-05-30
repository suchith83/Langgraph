import os
from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from openai import OpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def process(state: AgentState) -> AgentState:
    """This node will solve the request input"""
    messages = [{"role": "user", "content": msg.content} for msg in state["messages"]]
    
    completion = client.chat.completions.create(
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=messages,
    )
    response_text = completion.choices[0].message.content
    state["messages"].append(AIMessage(content=response_text))
    print(f"\nAI: {response_text}")
    print("CURRENT STATE:", state["messages"])
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

conversation_history = []

user_input = input("Enter: ")
while user_input.lower() != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": conversation_history})
    # print(result["messages"])
    conversation_history = result["messages"]
    user_input = input("Enter: ")

with open("logging.txt", "w") as f:
    f.write("Your conversation history:\n")
    for msg in conversation_history:
        if isinstance(msg, HumanMessage):
            f.write(f"You: {msg.content}\n")
        elif isinstance(msg, AIMessage):
            f.write(f"AI: {msg.content}\n\n")
    f.write("End of conversation.\n")
print("Conversation history saved to logging.txt")