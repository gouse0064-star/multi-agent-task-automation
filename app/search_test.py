
import os

from dotenv import load_dotenv
from langchain_tavily import TavilySearch


def main():
    load_dotenv()

    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError(
            "TAVILY_API_KEY is missing. Check your root .env file."
        )

    search_tool = TavilySearch(
        max_results=5,
        topic="general",
    )

    query = input("Enter a web search query: ").strip()

    if not query:
        print("Please enter a search query.")
        return

    print("\nSearching the web...")

    response = search_tool.invoke({"query": query})

    results = response.get("results", [])

    if not results:
        print("No search results were returned.")
        return

    print("\n===== LIVE SEARCH RESULTS =====")

    for index, item in enumerate(results, start=1):
        print(f"\n{index}. {item.get('title', 'Untitled')}")
        print(f"URL: {item.get('url', 'No URL')}")
        print(f"Summary: {item.get('content', 'No summary')}")


if __name__ == "__main__":
    main()
