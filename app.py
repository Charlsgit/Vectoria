import streamlit as st
from ai import ask_ai


# -------------------------
# Page Configuration
# -------------------------

st.set_page_config(
    page_title="Vectoria",
    page_icon="🤖"
)


# -------------------------
# Title
# -------------------------

st.title("🤖 Vectoria")

st.write("Your personal AI assistant")


# -------------------------
# Conversation History
# -------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------------------------
# Display Previous Messages
# -------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# -------------------------
# Chat Input
# -------------------------

prompt = st.chat_input("Ask me something...")


if prompt:

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    # Ask AI
    response = ask_ai(prompt)

    # Display AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.write(response)