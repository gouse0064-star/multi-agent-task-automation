
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os


class TaskState(TypedDict):
    task: str
    response: str


def ai_agent(state: TaskState) -> dict:
    """Process the task using the Groq language model."""

    load_dotenv()

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    result = model.invoke(
        f"""
        You are an intelligent task assistant.

        Understand the user's task and provide a useful,
        structured response with clear, actionable steps.

        User task: {state['task']}
        """
    )

    return {"response": result.content}


def build_graph():
    """Build and compile the LangGraph workflow."""

    graph = StateGraph(TaskState)

    graph.add_node("ai_agent", ai_agent)

    graph.add_edge(START, "ai_agent")
    graph.add_edge("ai_agent", END)

    return graph.compile()


def run_task(task: str) -> dict:
    workflow = build_graph()

    return workflow.invoke({
        "task": task,
        "response": "",
    })
