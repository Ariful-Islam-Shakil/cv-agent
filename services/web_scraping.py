# services/linkedin_service.py
import requests
from bs4 import BeautifulSoup
from services.groq_services import create_groq_client, update_conversation_history, get_response
def get_full_job_post_text(linkedin_url: str) -> str:
    """
    Retrieve the full visible text from a LinkedIn job post.
    
    Args:
        linkedin_url (str): LinkedIn job post URL.
        
    Returns:
        str: Full page text.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(linkedin_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching page: {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    # Get all visible text
    for script in soup(["script", "style"]):
        script.decompose()  # remove scripts/styles

    text = soup.get_text(separator="\n")
    # Clean up extra whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    full_text = "\n".join(lines)

    return full_text


def get_job_summary(text):
    client = create_groq_client()
    history = []
    content = f"""
        You are job post summarizer. I have a raw job post text. 
        The job post is :\n\n
        {text}
        \n\n
        your task is to make a summary of the job post with necessary informations.
    """
    history = get_response(client, message=content, history=history)
    return history[-1]