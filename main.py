import streamlit as st
from loguru import logger
from services.groq_services import create_groq_client, get_response, update_conversation_history
st.title("Hello, Its ayour CV Agent")
col1, col2 = st.columns(2)
General_chat_history = []
CV_chat_history = []
client = create_groq_client()
General_chat_history = update_conversation_history(history=General_chat_history, role="system", content="You are a helpfull assistant.")

with col1:
    st.subheader("General Chat")
    for message in General_chat_history:
        logger.info("*****")
        logger.error("Type: ", message.type)
        logger.error("contents: ", message.content)
        logger.info("messages: ", message)
        logger.info("*****")
        if message.type == "user":
            st.markdown(f"**You:** {message.content}")
        elif message.type == "assistant":
            st.markdown(f"**AI:** {message.content}")
    
    user_input = st.text_input("You: ", key="general_chat")
    if user_input:
        General_chat_history = get_response(client=client, message = user_input, history=General_chat_history)


with col2:
    st.subheader("Chat about you CV")