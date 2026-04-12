
from IPython.core.debugger import prompt
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict



load_dotenv()

# Model
model = ChatGoogleGenerativeAI(model='gemini-3-flash-preview')

class BlogState(TypedDict):
    title: str
    content: str
    outline: str

def create_outline(state: BlogState):
    title = state['title']

    prompt = f'generate a detailed outline for a blog on the topic:\n{title}'
    outline = model.invoke(prompt).content
    state['outline'] = outline

    return state

def create_blog(state: BlogState) -> BlogState:
    title = state['title']
    outline = state['outline']

    prompt = f'generate a detailed blog on the topic: \n{title} using the following outline: \n{outline}'
    content = model.invoke(prompt).content
    state['content'] = content

    return state

graph = StateGraph(BlogState)

# node
graph.add_node('create_outline_node', create_outline)
graph.add_node('create_blog_node', create_blog)

# Edges
graph.add_edge(START, 'create_outline_node')
graph.add_edge('create_outline_node', 'create_blog_node')
graph.add_edge('create_blog_node', END)

# Compile
workflow = graph.compile()

initial_state = {
    'title': 'Rise of AI in India',
}

result = workflow.invoke(initial_state)

print(result)