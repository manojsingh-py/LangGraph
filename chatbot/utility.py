import uuid

import streamlit as st


# -------------------
# Helper
# -------------------


def generate_thread_id():

    return str(uuid.uuid4())


def reset_chat():

    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []


def add_thread(thread_id):

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


def retrieve_all_threads(checkpointer):
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)