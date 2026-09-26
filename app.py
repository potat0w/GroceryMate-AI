import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from chatbot import get_response


def format_response(result) -> str:
    items = "\n".join(f"- {item}" for item in result.shopping_list)
    return (
        f"{result.answer}\n\n"
        f"**Category:** {result.category}\n\n"
        f"**Shopping List:**\n{items}\n\n"
        f"**Estimated Cost:** ৳{result.estimated_cost_bdt:.2f}\n\n"
        f"**Confidence:** {result.confidence:.2f}"
    )


st.set_page_config(page_title="Grocery Budget Planner", page_icon="🛒")
st.header("🛒 Grocery Budget Planner")
st.write(
    "Plan weekly meals, find ingredient substitutions, "
    "and estimate grocery costs in Bangladeshi Taka."
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    with st.chat_message(role):
        st.markdown(msg.content)

with st.sidebar:
    st.subheader("Chat History")
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    if not st.session_state.chat_history:
        st.write("(empty)")
    else:
        for msg in st.session_state.chat_history:
            role = "AI" if isinstance(msg, AIMessage) else "Human"
            st.markdown(f"**{role}:** {msg.content}")

if user_input := st.chat_input("Ask about your groceries"):
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.write(user_input)

    response = format_response(get_response(user_input))
    st.session_state.chat_history.append(AIMessage(content=response))

    with st.chat_message("assistant"):
        st.markdown(response)
