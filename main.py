# main.py
import streamlit as st
from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage
from services.groq_services import create_groq_client, get_response, update_conversation_history, get_cv_response
from services.web_scraping import get_full_job_post_text, get_job_summary
from services.file_handle import read_file
from loguru import logger
import tempfile

st.set_page_config(page_title="CV Agent", layout="wide")
st.title("Hello, It's your CV Agent")

# --- Initialize session state ---
if "General_chat_history" not in st.session_state:
    st.session_state.General_chat_history = []
    st.session_state.General_chat_history = update_conversation_history(
        history=st.session_state.General_chat_history,
        role="system",
        content="You are a helpful assistant."
    )

if "CV_chat_history" not in st.session_state:
    st.session_state.CV_chat_history = []

if "client" not in st.session_state:
    st.session_state.client = create_groq_client()

# ---------------- Sidebar ----------------
st.sidebar.header("Settings")

# Upload CV file
uploaded_file = st.sidebar.file_uploader("Upload your CV", type=["txt", "pdf", "docx"])
cv_text = ""
if uploaded_file is not None:
    if uploaded_file.type == "text/plain":
        cv_text = uploaded_file.read().decode("utf-8")
    else:
        # Save to temp file for pdf/docx
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        cv_text = read_file(tmp_path)
        # logger.error(cv_text)
    st.sidebar.success("CV uploaded successfully!")

# Input LinkedIn job post link
job_link = st.sidebar.text_input("Paste LinkedIn job post URL:")
job_text = ""
if job_link:
    job_text = get_full_job_post_text(job_link)
    job_text = get_job_summary(job_text)
    logger.error(job_text)
    st.sidebar.success("Job post loaded!")

# ---------------- Tabs (Navbar) ----------------
tabs = st.tabs(["General Chat", "CV Chat"])

# ---------------- General Chat ----------------
with tabs[0]:
    st.subheader("General Chat")
    
    # Input box
    if user_input := st.chat_input("Say something..."):
        st.session_state.General_chat_history = get_response(
            client=st.session_state.client,
            message=user_input,
            history=st.session_state.General_chat_history
        )
        st.rerun()

    # Messages container (scrollable)
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.General_chat_history[::-1]:
            if isinstance(msg, HumanMessage):
                st.chat_message("user").write(msg.content)
            elif isinstance(msg, AIMessage):
                st.chat_message("assistant").write(msg.content)
# ---------------- CV Chat ----------------
with tabs[1]:
    st.subheader("CV Chat")

    # Check if CV file and job post text are ready
    if not (cv_text and job_text):
        st.info("Please upload your CV and enter a LinkedIn job post URL to start the CV chat.")
    else:
        # Initialize CV chat with system message containing CV + job post
        if not st.session_state.CV_chat_history:
            system_content = "You are expected to function as a supportive assistant in the creation of a formal cover letter for a job application.\n"
            system_content += f"\nCandidate CV:\n{cv_text}"
            system_content += f"\nJob Description:\n{job_text}"
            system_content += f"\nPlease ensure that your response is tailored to the specific job posting, based on the skills and qualifications outlined in the candidate's CV, and presented in a concise manner."
            st.session_state.CV_chat_history = update_conversation_history(
                history=st.session_state.CV_chat_history,
                role="system",
                content=system_content
            )
            logger.info("CV chat system message initialized.")

        # Input box
        if cv_input := st.chat_input("Ask about your CV..."):
            st.session_state.CV_chat_history = get_cv_response(
                client=st.session_state.client,
                message=cv_input,
                history=st.session_state.CV_chat_history
            )
            st.rerun()

        # Messages container
        cv_container = st.container()
        with cv_container:
            for msg in st.session_state.CV_chat_history[::-1]:
                if isinstance(msg, HumanMessage):
                    st.chat_message("user").write(msg.content)
                elif isinstance(msg, AIMessage):
                    st.chat_message("assistant").write(msg.content)
