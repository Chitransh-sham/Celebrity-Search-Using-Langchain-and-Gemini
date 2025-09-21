import os
from constant import gemini_key
# from langchain.llms import gemini
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

os.environ["GOOGLE_API_KEY"] = gemini_key

# initailise streamlit app
st.title("My First AI agent ")
st.subheader("Using Langchain and Gemini")

input_text = st.text_input("Search your query here !")


# gemini LLMS
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.8)


if input_text:
    response = llm.invoke(input_text) 
    st.write(response.content)
    # response = llm.chat.completions.create(
    #     model="gpt-4",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": input_text
    #         }
    #     ]
    # )
