
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


def main():
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Check your root .env file."
        )

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.2,
        api_key=api_key,
    )

    response = model.invoke(
        "Explain what a multi-agent AI system is in three sentences."
    )

    print("\n===== GROQ AI RESPONSE =====")
    print(response.content)


if __name__ == "__main__":
    main()
