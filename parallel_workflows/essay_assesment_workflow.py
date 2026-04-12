
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import operator

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
import os

load_dotenv()

# Model
llm = HuggingFaceEndpoint(
    repo_id=os.getenv('HUGGINGFACE_REPO_ID'),
    task=os.getenv('HUGGINGFACE_TASK'),
    temperature=0.5
)

model = ChatHuggingFace(llm=llm)

class EvaluationSchema(BaseModel):
    feedback: str = Field(description='Detailed feedback for the eassy')
    score: int = Field(description='Score out of 10, ge=0, le=10')

# structured_model = model.with_structured_output(EvaluationSchema)

structured_model = model.with_structured_output(
    EvaluationSchema.model_json_schema(),
    method="json_schema"
)

essay = """Artificial Intelligence (AI) is rapidly transforming the world, and **India is emerging as one of the key players in adopting and developing AI technologies**. With its strong IT industry, large talent pool, and growing digital infrastructure, AI is playing an increasingly important role in shaping India’s economy, governance, education, healthcare, and daily life. 🇮🇳🤖

One of the most significant roles of AI in India is in the **healthcare sector**. AI-powered tools are helping doctors diagnose diseases more accurately and quickly. Technologies such as medical imaging analysis, predictive health monitoring, and virtual health assistants are improving patient care, especially in rural areas where access to specialist doctors is limited. AI is also supporting drug discovery and improving hospital management systems, making healthcare more efficient and affordable.

AI is also transforming **education in India**. With the help of intelligent learning platforms, students can now receive personalized learning experiences based on their abilities and pace. AI-based applications provide interactive content, automated assessments, and real-time feedback to students. These tools are especially useful in bridging the gap between urban and rural education systems and making quality learning accessible to everyone. 📚✨

In the field of **agriculture**, AI is helping farmers increase productivity and reduce risks. Smart farming techniques powered by AI can analyze soil conditions, weather patterns, crop health, and irrigation needs. Farmers can receive timely advice on crop selection, pest control, and fertilizer use through AI-driven mobile applications. This improves crop yield and supports sustainable agricultural practices, which is crucial for a country like India where agriculture employs a large portion of the population.

AI is also playing an important role in **governance and public services**. Government initiatives are increasingly using AI to improve decision-making, enhance transparency, and deliver services efficiently. AI-based systems help in traffic management, smart city development, fraud detection, and digital identity verification. These technologies are making government services faster, more reliable, and citizen-friendly. 🚦🏙️

India’s **economy and employment sector** are also benefiting from AI adoption. AI is creating new job opportunities in areas such as data science, machine learning, robotics, and automation. At the same time, it is improving productivity across industries like banking, manufacturing, retail, and logistics. Startups in India are actively developing innovative AI solutions, contributing to economic growth and global competitiveness.

However, the growth of AI also brings certain challenges. Issues such as data privacy, ethical concerns, job displacement due to automation, and the need for skilled professionals must be addressed carefully. The government and private sector need to work together to ensure responsible AI development and proper training programs for the workforce.

In conclusion, AI is playing a transformative role in India’s development by improving healthcare, education, agriculture, governance, and economic growth. With continued investment in technology, infrastructure, and skill development, India has the potential to become a global leader in artificial intelligence while ensuring inclusive and sustainable progress for its citizens. 🚀
"""

prompt = f"""
Evaluate the language quality of the following essay and provide a feedback and assign a score out of 10 \n {essay}
"""
# res = structured_model.invoke(prompt)
# res

class EssayState(TypedDict):
    essay: str
    language_feedback: str
    analysis_feedback: str
    clarity_feedback: str
    overall_feedback: str
    individual_score: Annotated[list[int], operator.add]
    avg_score: float

def evaluate_language(state: EssayState) -> EssayState:
    prompt = f"Evaluate the language quality of the following essay and provide a feedback and assign a score out of 10 \n {state['essay']}\n"
    output = structured_model.invoke(prompt)

    return {
    "language_feedback": output.feedback,
    "individual_score": [output.score]
}


def evaluate_analysis(state: EssayState) -> EssayState:
    prompt = f"Evaluate the depth of analysis of the following essay and provide a feedback and assign a score out of 10 \n {state['essay']}\n"
    output = structured_model.invoke(prompt)

    return {
    "analysis_feedback": output.feedback,
    "individual_score": [output.score]
}

def evaluate_thought(state: EssayState) -> EssayState:
    prompt = f"Evaluate the clarity of thought of the following essay and provide a feedback and assign a score out of 10 \n {state['essay']}\n"
    output = structured_model.invoke(prompt)

    return {
    "clarity_feedback": output.feedback,
    "individual_score": [output.score]
}

def final_evaluation(state: EssayState) -> EssayState:
    #Summary feedback
    prompt = (f"based on the following feebdack create a summarized feedback \n "
              f"language feedback - {state['language_feedback']} \n "
              f"depth of analysis - {state['analysis_feedback']} \n "
              f"clarity feedback - {state['clarity_feedback']} \n ")
    overall_feedback = structured_model.invoke(prompt)

    # Avg calculation
    avg_score = sum(state['individual_score']) / len(state['individual_score'])

    return {
    "overall_feedback": overall_feedback,
    "avg_score": avg_score
}

graph = StateGraph(EssayState)

graph.add_node('evaluate_language', evaluate_language)
graph.add_node('evaluate_analysis', evaluate_analysis)
graph.add_node('evaluate_thought', evaluate_thought)
graph.add_node('final_evaluation', final_evaluation)

graph.add_edge(START, 'evaluate_language')
graph.add_edge(START, 'evaluate_analysis')
graph.add_edge(START, 'evaluate_thought')

graph.add_edge('evaluate_language', 'final_evaluation')
graph.add_edge('evaluate_analysis', 'final_evaluation')
graph.add_edge('evaluate_thought', 'final_evaluation')

graph.add_edge('final_evaluation', END)

workflow = graph.compile()

intial_state = {
    'essay': essay
}
result = workflow.invoke(intial_state)
print(result)