import streamlit as st
import requests
from chatbot import ChatbotService
from state import ChatbotState

# --- Page Configuration ---
st.set_page_config(
    page_title="CV Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Functions ---
@st.cache_resource
def get_chatbot():
    """Initializes the chatbot service."""
    return ChatbotService()

def check_api():
    """Checks if the backend API is running."""
    try:
        response = requests.get("http://localhost:3010/health", timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# --- Main Application ---
st.title("🤖 CV Chatbot Assistant")
st.caption("Smart search and analysis of candidate profiles")

# Check if the API is running
if not check_api():
    st.error("⚠️ API is not running! Please run: python3 rag_api.py")
    st.stop()

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["type"]):
        st.write(msg["content"])

# Get user input
if user_input := st.chat_input("Ask a question about a candidate's CV..."):
    # Add user message to state and display it
    st.session_state.messages.append({"type": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Process and display the bot's response
    with st.chat_message("bot"):
        with st.spinner("Thinking..."):
            try:
                chatbot = get_chatbot()
                
                # Prepare the state for the chatbot graph
                state = ChatbotState(
                    raw_question=user_input,
                    rephrased_question="",
                    sub_questions=[],
                    refined_contexts=[],
                    conversation_history=[],
                    answer=""
                )

                # Invoke the chatbot and get the result
                result = chatbot.compiled_graph.invoke(state)
                answer = result.get('answer', 'No answer found.')

                # Display the answer and add it to the session state
                st.write(answer)
                st.session_state.messages.append({"type": "bot", "content": answer})

            except Exception as e:
                error_message = f"Sorry, an error occurred: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"type": "bot", "content": error_message})