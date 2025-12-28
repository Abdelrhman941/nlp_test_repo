# app/ui.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

# Page config
st.set_page_config(
    page_title="Pet Health Assistant",
    page_icon="🐾",
    layout="centered"
)

# Header
st.title("🐾 Pet Health AI Assistant")
st.markdown("*Ask me anything about your pet's health!*")

# Load chatbot (cached)
@st.cache_resource
def load_chatbot():
    from rag.chatbot import rag_chatbot
    return rag_chatbot

with st.spinner("🔄 Loading AI model... (first time only)"):
    rag_chatbot = load_chatbot()

st.success("✅ Ready to help!")
st.markdown("---")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "👋 Hello! How can I help with your pet today?"
    }]

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your question..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = rag_chatbot(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    **Pet Health Assistant** helps with:
    - 🐕 Dog health questions
    - 🐈 Cat care tips
    - 🏥 General pet advice

    ⚠️ *Always consult a real vet for serious issues!*
    """)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "👋 Chat cleared! How can I help?"
        }]
        st.rerun()
