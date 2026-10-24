from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def pick_llm(level: str):
    if level.lower() == "low":
        llm = ChatOpenAI(
            model_name="gpt-5.6-luna",
            temperature=0.1,
            use_responses_api=True,
        )
    elif level.lower() == "medium":
        llm = ChatOpenAI(
            model_name="gpt-5.6-terra",
            temperature=0.1,
            use_responses_api=True,
        )
    elif level.lower() == "high":
        llm = ChatOpenAI(
            model_name="gpt-5.6-sol",
            temperature=0.1,
            use_responses_api=True,
        )
    else:
        raise ValueError("Invalid level. Please choose from 'low', 'medium', or 'high'.")

    return llm

    