# import os
# from constant import gemini_key
# # from langchain.llms import gemini
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.memory import ConversationBufferMemory

# import streamlit as st
# import json
# import ast

# os.environ["GOOGLE_API_KEY"] = gemini_key

# # initailise streamlit app
# st.title("Search Celebrity  Info")


# input_text = st.text_input("Enter Name here !")

# # Prompt template
# prompt = PromptTemplate(
#     input_variables=["name"],
#     template="""
# You are a helpful assistant. Provide information about the celebrity {name} in **strict JSON format only**:
# {{
#     "bio": "Short biography of the celebrity",
#     "dob": "Date of birth",
#     "image_url": "Link to profile picture"
# }}

# Do NOT include any text outside the JSON.
# """
# )

# # memory
# memory = ConversationBufferMemory(input_key="name", memory_key="chat_history", return_messages=True)


# # gemini LLMS
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.8)
# chain = LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=False)

# if input_text:
#     raw_result = chain.invoke({"name": input_text}).strip()
#     if raw_result.startswith("```") and raw_result.endswith("```"):
#       raw_result = "\n".join(raw_result.split("\n")[1:-1])
#     try:
#         data = json.loads(raw_result)
#     except json.JSONDecodeError:
#         # fallback: sometimes LLM returns single quotes or minor formatting issues
#         try:
#             data = ast.literal_eval(raw_result)
#         except Exception:
#             st.error("Could not parse LLM output. Raw output:")
#             st.write(raw_result)
#             data = None
#     if data:
#         st.write("**Bio:**", data.get("bio", "N/A"))
#         st.write("**Date of Birth:**", data.get("dob", "N/A"))
#         image_url = data.get("image_url")
#         if image_url:
#             st.image(image_url, width=300)
#         else:
#             st.write("No image found.")

import os
import json
import ast
import streamlit as st
from constant import gemini_key
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import messages_from_dict, messages_to_dict


# Set API key
os.environ["GOOGLE_API_KEY"] = gemini_key

# Streamlit app
st.title("Celebrity Info Chatbot")
st.subheader("Search and remember multiple celebrity queries!")

# User input
input_text = st.text_input("Enter Celebrity Name:")

# Prompt template
prompt = PromptTemplate(
    input_variables=["name"],
    template="""
You are a helpful assistant. Provide information about the celebrity {name} in **strict JSON format only**:
{{
    "bio": "Short biography of the celebrity",
    "dob": "Date of birth",
    "image_url": "Link to profile picture"
}}
Do NOT include any text outside the JSON.
"""
)

# Conversation memory
memory = ConversationBufferMemory(
    input_key="name",
    memory_key="chat_history",
    return_messages=True
)

# Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.8)

# Create a RunnableSequence: prompt | llm
chain = prompt | llm

# Function to run query and update memory
def run_query(name):
    # Include memory in input
    input_dict = {"name": name}
    if memory.chat_memory.messages:
        input_dict["chat_history"] = messages_to_dict(memory.chat_memory.messages)

    # Get LLM response
    raw_result = chain.invoke({"name": input_text}).content.strip()

    # Remove backticks if present
    if raw_result.startswith("```") and raw_result.endswith("```"):
        raw_result = "\n".join(raw_result.split("\n")[1:-1])

    # Parse JSON safely
    try:
        data = json.loads(raw_result)
    except json.JSONDecodeError:
        try:
            data = ast.literal_eval(raw_result)
        except Exception:
            st.error("Could not parse LLM output. Raw output:")
            st.write(raw_result)
            data = None

    # Update memory
    memory.chat_memory.add_user_message(name)
    if data:
        memory.chat_memory.add_ai_message(raw_result)
    return data

# Run the query
if input_text:
    data = run_query(input_text)
    if data:
        st.write("**Bio:**", data.get("bio", "N/A"))
        st.write("**Date of Birth:**", data.get("dob", "N/A"))
        image_url = data.get("image_url")
        if image_url:
            st.image(image_url, width=300)
        else:
            st.write("No image found.")

# Display chat history
if memory.chat_memory.messages:
    st.write("### Chat History")
    for msg in memory.chat_memory.messages:
        st.write(f"{msg.type.capitalize()}: {msg.content}")
