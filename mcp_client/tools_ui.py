import sys
import os

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from chatbot_async import chat_workflow, checkpointer
from chatbot.utility import generate_thread_id, reset_chat, add_thread_id, load_conversation, get_recent_threads


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

# for thread_id in st.session_state['chat_threads']:
#     if st.sidebar.button(thread_id, key=thread_id):
#         st.session_state['thread_id'] = thread_id
#         message = load_conversation(chat_workflow, thread_id)
#
#         temp_msg = []
#
#         for msg in message:
#             if isinstance(msg, HumanMessage):
#                 role = 'user'
#             elif isinstance(msg, AIMessage):
#                 role = "assistant"
#             elif isinstance(msg, ToolMessage):
#                 continue
#
#             temp_msg.append({'role': role, 'content': msg.content})
#
#         st.session_state['message_history']= temp_msg


for thread_id in st.session_state['chat_threads']:

    if st.sidebar.button(thread_id, key=thread_id):

        st.session_state['thread_id'] = thread_id

        message = load_conversation(chat_workflow, thread_id)

        temp_msg = []

        for msg in message:

            if isinstance(msg, HumanMessage):
                role = "user"

            elif isinstance(msg, AIMessage):
                role = "assistant"

            else:
                continue

            temp_msg.append({
                "role": role,
                "content": msg.content
            })

        st.session_state['message_history'] = temp_msg

        st.rerun()

# ============================ Main UI ============================
# Render history

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
        "messages": [HumanMessage(content=user_input)]
    }

    config = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        },
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        }
    }


    # Assistant streaming block
    with st.chat_message("assistant"):

        status_holder = {"box": None}
        response_holder = {"text": ""}


        def extract_text(content):
            """Normalize LangGraph message content into string"""

            if isinstance(content, str):
                return content

            if isinstance(content, list):
                text_parts = []

                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))

                return "".join(text_parts)

            return ""


        def ai_only_stream():

            for message_chunk, metadata in chat_workflow.stream(
                    input=int_msg,
                    config=config,
                    stream_mode="messages"
            ):

                # Tool execution status
                if isinstance(message_chunk, ToolMessage):

                    tool_name = getattr(message_chunk, "name", "tool")

                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …",
                            expanded=True
                        )

                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                    # OPTIONAL: show tool output
                    tool_output = extract_text(message_chunk.content)

                    if tool_output:
                        yield f"\n\n🔧 Tool Output:\n{tool_output}\n\n"


                # Assistant streaming tokens
                elif isinstance(message_chunk, AIMessage):

                    text_chunk = extract_text(message_chunk.content)

                    if text_chunk:
                        response_holder["text"] += text_chunk
                        yield text_chunk


        ai_message = st.write_stream(ai_only_stream())

        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished",
                state="complete",
                expanded=False
            )

    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": ai_message
        }
    )
