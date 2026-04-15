import uuid

import streamlit as st



def generate_thread_id():

    return str(uuid.uuid4())


def reset_chat():

    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread_id(st.session_state['thread_id'])
    st.session_state['message_history'] = []


def add_thread_id(thread_id):

    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = []

    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(chat_workflow, thread_id):

    config = {"configurable": {"thread_id": thread_id}}
    state = chat_workflow.get_state(config=config)

    if not state.values:
        return []

    return state.values.get("message", [])


def get_recent_threads(checkpointer):

    all_threads = set()
    for chk_point in checkpointer.list(None):
        all_threads.add(chk_point.config['configurable']['thread_id'])

    return  list(all_threads)