import streamlit as st
from pydantic import ValidationError

from app.agent.orchestrator import run_agent
from app.config import get_settings
from app.ui.chat import render_chat_history
from app.ui.sidebar import render_sidebar

st.set_page_config(page_title="Stock Insights Assistant", page_icon="📈", layout="wide")
st.title("📈 Stock Insights Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

render_sidebar()
render_chat_history(st.session_state.messages)

if prompt := st.chat_input("Ask about any stock or company..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            try:
                settings = get_settings()
                response = run_agent(prompt, st.session_state.messages[:-1], settings)
            except ValidationError:
                response = (
                    "Configuration error: missing API keys. "
                    "Please ensure OPENAI_API_KEY and FINNHUB_API_KEY are set in your .env file."
                )
            except Exception as exc:
                response = f"An unexpected error occurred: {exc}"
        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
