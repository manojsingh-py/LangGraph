import os
import sqlite3

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict,Annotated
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver



class ChatState(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]

load_dotenv()

# Model
# model = ChatGoogleGenerativeAI(model='gemini-3-flash-preview')

llm = HuggingFaceEndpoint(
    repo_id=os.getenv('HUGGINGFACE_REPO_ID'),
    task=os.getenv('HUGGINGFACE_TASK'),
    temperature=0.5
)

model = ChatHuggingFace(llm=llm)



def chat_node(state: ChatState) -> ChatState:
    # take user query state
    message = state['message']
    # send to llm
    res = model.invoke(message)

    #response store state
    return {'message': [res]}




graph = StateGraph(ChatState)

# Node
graph.add_node('chat_node', chat_node)

# Edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)


# Checkpointer
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# Compiler
chat_workflow = graph.compile(checkpointer=checkpointer)




# all_threads = set()
# for chk_point in checkpointer.list(None):
#     all_threads.add(chk_point.config['configurable']['thread_id'])
#
#
# print(list(all_threads))

# config = {'configurable': {'thread_id': 'thread-2'}}
# int_msg = {
#         'message': [HumanMessage(content='my name is rohan')],
#     }
# response = chat_workflow.invoke(input=int_msg, config=config)
#
# print(chat_workflow.get_state(config=config).values)


# thread_id = '1'
#
# while True:
#     user_message = input('Enter your message: ')
#     print('User:', user_message)
#
#     if user_message.strip().lower() in ['exit', 'quit', 'bye']:
#         break
#
#     int_msg = {
#         'message': [HumanMessage(content=user_message)]
#     }
#     config = {'configurable': {'thread_id': thread_id}}
#     response = workflow.invoke(int_msg, config=config)
#
#     print('Bot:', response['message'][-1].content[0]['text'])
#
#
#
# workflow.get_state(config=config)
#
