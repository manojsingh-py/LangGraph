from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain_core.tools import StructuredTool

load_dotenv()  # Load environment variables from .env file

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# MCP client for local FastMCP server
client = MultiServerMCPClient(
    {
        # "arith": {
        #     "transport": "stdio",
        #     "command": "python3",
        #     "args": ["/Users/nitish/Desktop/mcp-math-server/main.py"],
        # },
        "expense": {
            "transport": "streamable_http",  # if this fails, try "sse"
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        }
    }
)


# state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


async def build_graph():

    tools = await client.get_tools()

    tools = [t for t in tools if "expense" not in t.name.lower()]

    llm_with_tools = llm.bind_tools(tools)


    # nodes
    async def chat_node(state: ChatState):

        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {'messages': [response]}

    tool_node = ToolNode(tools)

    # defining graph and nodes
    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    # defining graph connections
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")
    graph.add_edge("chat_node", END)

    chatbot = graph.compile()

    return chatbot

async def main():

    chatbot = await build_graph()

    init_state = {
            "messages": [
                HumanMessage(
                    content="Give me all my expenses for the month of Nov from 1 Nov to 30 Nov"
                )
            ]
        }
    config = {
        "configurable": {
            "thread_id": "expense-session-1"
        }
    }
    # running the graph
    result = await chatbot.ainvoke(input=init_state, config=config)

    print(result['messages'][-1].content)

if __name__ == '__main__':
    asyncio.run(main())