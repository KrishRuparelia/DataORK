import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

st.set_page_config(
    page_title="DataOrk",
    page_icon="D",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_resource
def get_data_agent() -> Any:
    from agents.data_agent import data_agent

    return data_agent


def message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text = [
            block["text"]
            for block in content
            if isinstance(block, dict) and isinstance(block.get("text"), str)
        ]
        if text:
            return "\n".join(text)
    return str(content)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.markdown("# DataOrk")
    st.caption("Your data, in plain language.")
    st.divider()
    st.markdown("### Workspace")
    st.markdown("**SQL analyst**")
    st.caption("Ask questions about your PostgreSQL data.")
    st.markdown("**ETL analyst**")
    st.caption("Extract data from APIs or transform files.")
    st.divider()
    st.markdown("### Connections")
    st.write(
        "OpenAI",
        "Connected" if os.getenv("OPENAI_API_KEY") else "API key missing",
    )
    database_configured = all(
        os.getenv(key) for key in ("host", "port", "user", "password", "database")
    )
    st.write(
        "PostgreSQL",
        "Configured" if database_configured else "Not configured",
    )
    st.caption("Connection details are read from your local .env file.")
    st.divider()
    if st.button(
        "New conversation",
        icon=":material/add:",
        width="stretch",
    ):
        st.session_state.chat_history = []
        st.rerun()

st.badge("Data workspace", color="blue")
st.title("Ask your data.")
st.caption(
    "Explore your database or get an ETL task done using natural language."
)
st.caption("SQL · ETL · PostgreSQL")

if not st.session_state.chat_history:
    st.markdown("#### Try asking")
    suggestions = [
        "What payment methods are in the database?",
        "Show rides grouped by status.",
        "Fetch Pokémon data and save it as CSV.",
    ]
    suggestion_columns = st.columns(len(suggestions))
    for column, suggestion in zip(suggestion_columns, suggestions):
        with column:
            if st.button(suggestion, width="stretch"):
                st.session_state.pending_prompt = suggestion

for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])
        if entry.get("route"):
            st.caption(f"Handled by {entry['route']} analyst")

prompt = st.chat_input("Ask a question or describe an ETL task...")
if not prompt:
    prompt = st.session_state.pop("pending_prompt", None)

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not os.getenv("OPENAI_API_KEY"):
            error = "OPENAI_API_KEY is missing. Add it to your local .env file and restart the app."
            st.error(error)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": error}
            )
        else:
            with st.status("Working on your request...", expanded=True) as status:
                try:
                    result = get_data_agent().invoke(
                        {
                            "messages": [HumanMessage(content=prompt)],
                            "route_response": "",
                        }
                    )
                    route = result.get("route_response", "")
                    messages = result.get("messages", [])
                    answer = message_text(messages[-1].content) if messages else ""
                    if not answer:
                        raise RuntimeError(
                            "The agent completed without returning an answer."
                        )
                    status.update(
                        label=f"Complete · {route.upper()} analyst",
                        state="complete",
                        expanded=False,
                    )
                    st.markdown(answer)
                    st.caption(f"Handled by {route} analyst")
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "route": route,
                        }
                    )
                except Exception as exc:
                    status.update(label="Request failed", state="error")
                    st.error(f"Could not complete the request: {exc}")
                    st.exception(exc)
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": f"Request failed: {exc}",
                        }
                    )
