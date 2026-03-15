import streamlit as st


def render_chat_history(messages: list[dict]) -> None:
    """Render the conversation history using Streamlit chat message components."""
    for message in messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
