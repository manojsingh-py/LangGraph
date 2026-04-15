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
    st.session_state['message_history'].append(
        {
            'role': 'user',
            'content': user_input
        }
    )
    with st.chat_message('user'):
        st.text(user_input)

    thread_id = 1

    int_msg = {
        'message': [HumanMessage(content=user_input)]
    }
    config = {'configurable': {'thread_id': thread_id}}

    with st.chat_message("assistant"):
        message_stream = chat_workflow.stream(
            input=int_msg,
            config=config,
            stream_mode="messages"
        )

        ai_message = st.write_stream(
            msg.content for msg, _ in message_stream
        )

    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": ai_message
        }
    )
