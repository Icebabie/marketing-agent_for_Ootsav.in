import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from models import UserIntent

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7
)


def invoke_llm(messages):
    """
    Send the entire conversation to Gemini.
    """

    response = llm.invoke(messages)

    return response



def extract_user_intent(messages):

    structured_llm = llm.with_structured_output(UserIntent)

    response = structured_llm.invoke(messages)

    return response