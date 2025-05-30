from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os

load_dotenv()


class AgentState(TypedDict):
    messages: List[HumanMessage]


token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

# client = OpenAI(
#     base_url=endpoint,
#     api_key=token,
# )

llm = ChatOpenAI(model=model, base_url=endpoint, api_key=token)

def process(state: AgentState) -> AgentState:
    """This node will solve the request input"""
    response = llm.invoke(state["messages"])
    print(f"\nAI: {response.content}")
    return state



graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()



user_input = input("Enter: ")
# agent.invoke({"messages": [HumanMessage(content=user_input)]})

while user_input != "exit":
    agent.invoke({"messages": [HumanMessage(content=user_input)]})
    user_input = input("Enter: ")