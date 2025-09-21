# services/groq_services.py
import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.schema.messages import SystemMessage, HumanMessage, AIMessage
from loguru import logger
from dotenv import load_dotenv

# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Load the secrets
config = st.secrets

# Access the API key
GROQ_API_KEY = config["groq"]["api_key"]



def create_groq_client():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")
    client = ChatGroq(
        api_key=GROQ_API_KEY,
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.7,
        max_retries=3,
        streaming=False,
    )
    return client


def update_conversation_history(history, role, content):
    if role == "user":
        history.append(HumanMessage(content=content))
    elif role == "assistant":
        history.append(AIMessage(content=content))
    elif role == "system":
        history.append(SystemMessage(content=content))
    else:
        raise ValueError("Invalid role. Must be 'user', 'assistant', or 'system'")
    return history


def get_response(client, message, history):
    history = update_conversation_history(history=history, role="user", content=message)
    try:
        response = client.invoke(history)
        history = update_conversation_history(history=history, role="assistant", content=response.content)
        logger.info(f"Assistant: {response.content}")
        return history
    except Exception as e:
        logger.error(f"Error getting response from Groq client: {e}")
        # remove last user message if failed
        return history[:-1]


def get_cv_response(client, message, history):
    history = update_conversation_history(history=history, role="user", content=message)
    try:
        response = client.invoke(history)
        history = update_conversation_history(history=history, role="assistant", content=response.content)
        logger.info(f"Assistant: {response.content}")
        return history
    except Exception as e:
        logger.error(f"Error getting response from Groq client: {e}")
        # remove last user message if failed
        return history[:-1]