from typing import TypedDict, List
from langchain_core.messages import HumanMessage
from openai import OpenAI
# from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os

load_dotenv()


class AgentState(TypedDict):
    messages: List[HumanMessage]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# llm = ChatOpenAI(model="gpt-4o-mini")

# def process(state: AgentState) -> AgentState:
#     response = llm.invoke(state["messages"])
#     print(f"\nAI: {response.content}")
#     return state

def process2(state: AgentState) -> AgentState:
    # Convert LangChain messages to the format expected by OpenAI SDK
    messages = [{"role": "user", "content": msg.content} for msg in state["messages"]]
    
    completion = client.chat.completions.create(
        model="meta-llama/llama-3.3-8b-instruct:free",
        messages=messages,
        # extra_headers={
        #     "HTTP-Referer": "https://your-site-url.com",  # optional
        #     "X-Title": "Your Site Name",                   # optional
        # },
    )
    response_text = completion.choices[0].message.content
    print(f"\nAI: {response_text}")
    
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process2)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

user_input = input("Enter: ")
while user_input != "exit":
    agent.invoke({"messages": [HumanMessage(content=user_input)]})
    user_input = input("Enter: ")