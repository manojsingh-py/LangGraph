from token import STAR
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph


# Define state

class BMICalculator(TypedDict):
    weight: float
    height: float
    bmi: float

# Calculate bmi
def calculate_bmi(state: BMICalculator) -> BMICalculator:
    weight = state['weight']
    height = state['height']
    bmi = weight / (height**2)

    return BMICalculator(weight=weight, height=height, bmi=round(bmi, 2))


# Define graph

graph = StateGraph(BMICalculator)

# Add nodes

graph.add_node('calculate_bmi', calculate_bmi)


# Add edged

graph.add_edge(START, 'calculate_bmi')
graph.add_edge('calculate_bmi', END)

# Compile the graph
workflow = graph.compile()

# Execute the graph
initial_state = {'weight': 80, 'height': 1.40}
result = workflow.invoke(initial_state)

print(result)


# Visualize the graph
# from IPython.display import display, Image
# Image(workflow.get_graph().draw_mermaid_png())


# Alternative approach for PyCharm scripts

import webbrowser

graph_png = workflow.get_graph().draw_mermaid_png()

file_path = "workflow_graph.png"

with open(file_path, "wb") as f:
    f.write(graph_png)

webbrowser.open(file_path)

