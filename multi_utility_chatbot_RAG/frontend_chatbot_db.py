import streamlit as st
from langchain_core.messages import HumanMessage

from backend_chatbot_using_db import chat_workflow, checkpointer
from utility import generate_thread_id, reset_chat, add_thread_id, load_conversation, get_recent_threads


########################## Session Setup #######################################

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()


if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = get_recent_threads(checkpointer)


add_thread_id(st.session_state['thread_id'])


########################### Sidebar UI #######################################

st.sidebar.title('Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('Recent')

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(thread_id, key=thread_id):
        st.session_state['thread_id'] = thread_id
        message = load_conversation(chat_workflow, thread_id)

        temp_msg = []

        for msg in message:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'

            temp_msg.append({'role': role, 'content': msg.content})

        st.session_state['message_history']= temp_msg


# Loading conversation history
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


    int_msg = {
        'message': [HumanMessage(content=user_input)]
    }

    config = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        },
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        }
    }

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
