import json
import streamlit as st

from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_community.chat_message_histories import ChatMessageHistory


# ---------------------------
# Streamlit UI
# ---------------------------
st.title("Celebrity Info Chatbot (Ollama)")
st.subheader("Search and remember multiple celebrity queries!")


# ---------------------------
# User Input
# ---------------------------
input_text = st.text_input("Enter Celebrity Name:")


# ---------------------------
# Prompt Template
# ---------------------------
prompt = PromptTemplate(
    input_variables=["name"],
    template="""
Provide information about the celebrity {name} in **strict JSON only**:

{{
  "bio": "Short biography",
  "dob": "Date of birth",
  "image_url": "Valid image link"
}}

DO NOT include anything outside JSON.
"""
)


# ---------------------------
# Conversation Memory (Updated API)
# ---------------------------
memory = ChatMessageHistory()   # new system, replace ConversationBufferMemory


# ---------------------------
# Local LLM (Ollama)
# ---------------------------
llm = ChatOllama(
    model="llama3.1",      # make sure you did: ollama pull llama3.1
    temperature=0.7
)

# Combine prompt + llm
chain = prompt | llm


# ---------------------------
# Function to Query Model
# ---------------------------
def run_query(name):
    # Add chat history for context
    chat_history = memory.messages if memory.messages else []

    # Run model
    response = chain.invoke({"name": name})

    raw_output = response.content.strip()

    # Remove accidental code block
    if raw_output.startswith("```"):
        raw_output = "\n".join(raw_output.split("\n")[1:-1])

    # Try JSON parse
    try:
        data = json.loads(raw_output)
    except:
        st.error("Could not parse model output. Raw output:")
        st.write(raw_output)
        return None

    # Update memory
    memory.add_user_message(name)
    memory.add_ai_message(raw_output)

    return data


# ---------------------------
# When user clicks enter
# ---------------------------
if input_text:
    data = run_query(input_text)
    print(data)
    if data:
        st.write("### Result")
        st.write("**Bio:**", data.get("bio", "N/A"))
        st.write("**Date of Birth:**", data.get("dob", "N/A"))

        if data.get("image_url"):
            st.image(data["image_url"], width=300)
        else:
            st.write("No image available")


# ---------------------------
# Chat History Section
# ---------------------------
if memory.messages:
    st.write("### Chat History")
    for msg in memory.messages:
        sender = "User" if msg.type == "human" else "Assistant"
        st.write(f"**{sender}:** {msg.content}")
