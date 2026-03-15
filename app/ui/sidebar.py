import streamlit as st

_EXAMPLE_QUESTIONS = [
    "How is AAPL doing today?",
    "Compare TSLA and F",
    "What are Apple's key financial metrics?",
    "Any recent news about Microsoft?",
    "Find the ticker for Palantir",
    "What's the 52-week high for NVDA?",
]


def render_sidebar() -> None:
    """Render the sidebar with example questions and session controls."""
    with st.sidebar:
        st.header("Stock Insights Assistant")
        st.markdown("Ask natural language questions about any publicly traded stock.")

        st.subheader("Example questions")
        for question in _EXAMPLE_QUESTIONS:
            st.markdown(f"- *{question}*")

        st.divider()

        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
