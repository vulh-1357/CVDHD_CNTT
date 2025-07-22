import streamlit as st
from models import ChatbotInput
import httpx

# --- Page Configuration ---
st.set_page_config(
    page_title="CV Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Main Application ---
st.title("🤖 CV Chatbot Assistant")
st.caption("Smart search and analysis of candidate profiles")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if user_input := st.chat_input("Ask a question about a candidate's CV..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Process and display the bot's response
    with st.chat_message("bot"):
        with st.spinner("Thinking..."):
            try:
                chatbot_input = ChatbotInput(
                    raw_question=user_input,
                    rephrased_question="",
                    sub_questions=[],
                    refined_contexts=[],
                    conversation_history=[],
                    answer=""
                )

                try:
                    with httpx.Client(timeout=30.0) as client:
                        response = client.post(
                            "http://localhost:8008/chat",
                            json=chatbot_input.model_dump()
                        )
                        if response.status_code == 200:
                            answer = response.json().get("answer", "No answer found.")
                        else:
                            answer = "Sorry, I couldn't retrieve the answer. Please try again later."
                except httpx.TimeoutException:
                    answer = "Sorry, the request timed out. Please try again later."
                except httpx.ConnectError:
                    answer = "Sorry, I couldn't connect to the server. Please try again later."

                st.write(answer)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_message = f"Sorry, an error occurred: {str(e)}"
                st.error(error_message)
                # Add error message to chat history
                st.session_state.messages.append({"role": "assistant", "content": error_message})