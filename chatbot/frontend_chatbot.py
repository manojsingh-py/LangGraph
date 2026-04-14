import streamlit as st
from langchain_core.messages import HumanMessage

from backend_chatbot import chat_workflow



if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


for message in st.session_state['message_history']:
    with st.chat_message(message['role']    ):
        st.text(message['content'])

user_input = st.chat_input('Enter your message..')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    thread_id = 1

    int_msg = {
        'message': [HumanMessage(content=user_input)]
    }
    config = {'configurable': {'thread_id': thread_id}}
    response = chat_workflow.invoke(int_msg, config=config)

    st.session_state['message_history'].append({'role': 'assistant', 'content': response['message'][-1].content[0]['text']})

    with st.chat_message('assistant'):
        st.text(response['message'][-1].content[0]['text'])

