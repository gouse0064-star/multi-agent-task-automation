
import json
import os
from typing import TypedDict, List

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END


load_dotenv()

MODEL_NAME = "openai/gpt-oss-20b"


class TaskState(TypedDict):
    task: str
    selected_agents: List[str]
    results: List[dict]
    final_report: str


def get_model():
    """Create a Groq chat model."""
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Check your root .env file."
        )

    return ChatGroq(
        model=MODEL_NAME,
        temperature=0.2,
        api_key=api_key,
    )


def orchestrator(state: TaskState) -> dict:
    """Choose the agents required for the user's task."""

    model = get_model()

    response = model.invoke([
        SystemMessage(content="""
You are the orchestrator of a multi-agent task automation system.

Choose the specialized agents needed to complete the user's task.

Available agents:
- research: organize research requirements and identify information needed
- planning: create actionable steps and priorities
- analysis: compare options, reason about evidence, and evaluate findings
- verification: identify potential errors, missing details, and unsupported claims

Return ONLY a valid JSON object in this format:
{"agents": ["planning", "analysis"]}

Select one or more agents. Use only the exact agent names listed above.
Choose agents relevant to the task. Do not include explanations outside JSON.
"""),
        HumanMessage(content=f"User task: {state['task']}"),
    ])

    try:
        data = json.loads(response.content)
        allowed = {"research", "planning", "analysis", "verification"}

        selected = [
            agent for agent in data["agents"]
            if agent in allowed
        ]

        if not selected:
            selected = ["planning"]

    except (json.JSONDecodeError, KeyError, TypeError):
        selected = ["planning"]

    # Verification should review the completed agent outputs.
    if "verification" not in selected:
        selected.append("verification")

    print(f"\nOrchestrator selected: {', '.join(selected)}")

    return {"selected_agents": selected}


AGENT_INSTRUCTIONS = {
    "research": (
        "Organize the research needed for the task. Identify relevant "
        "topics, reliable source types, and information to collect. "
        "Do not claim you performed live web searches."
    ),
    "planning": (
        "Create a practical, ordered plan with clear steps, priorities, "
        "and expected outcomes."
    ),
    "analysis": (
        "Analyze the task carefully. Explain relevant factors, compare "
        "alternatives where appropriate, and state important assumptions."
    ),
    "verification": (
        "Review the task and the preceding agent results. Identify "
        "inconsistencies, missing information, unsupported claims, and "
        "specific improvements. Do not claim external verification."
    ),
}


def run_specialized_agent(state: TaskState, agent_name: str) -> dict:
    """Execute one selected AI agent and save its output."""

    previous_results = state.get("results", [])

    context = "\n\n".join(
        f"{item['agent']}:\n{item['output']}"
        for item in previous_results
    )

    model = get_model()

    response = model.invoke([
        SystemMessage(content=(
            f"You are the {agent_name.title()} Agent in a multi-agent "
            f"system.\n{AGENT_INSTRUCTIONS[agent_name]}\n"
            "Be specific, useful, and honest about limitations."
        )),
        HumanMessage(content=(
            f"User task:\n{state['task']}\n\n"
            f"Previous agent results:\n{context or 'None yet'}"
        )),
    ])

    result = {
        "agent": agent_name.title() + " Agent",
        "output": response.content,
    }

    print(f"\nCompleted: {result['agent']}")

    return {"results": previous_results + [result]}


def research_node(state: TaskState) -> dict:
    return run_specialized_agent(state, "research")


def planning_node(state: TaskState) -> dict:
    return run_specialized_agent(state, "planning")


def analysis_node(state: TaskState) -> dict:
    return run_specialized_agent(state, "analysis")


def verification_node(state: TaskState) -> dict:
    return run_specialized_agent(state, "verification")


def route_to_agents(state: TaskState) -> str:
    """Choose the first selected agent."""
    return state["selected_agents"][0]


def next_agent(state: TaskState) -> str:
    """Choose the next selected agent that has not run."""
    completed = {
        item["agent"].replace(" Agent", "").lower()
        for item in state["results"]
    }

    for agent in state["selected_agents"]:
        if agent not in completed:
            return agent

    return "finish"


def build_graph():
    graph = StateGraph(TaskState)

    graph.add_node("orchestrator", orchestrator)
    graph.add_node("research", research_node)
    graph.add_node("planning", planning_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("verification", verification_node)

    graph.add_edge(START, "orchestrator")

    graph.add_conditional_edges(
        "orchestrator",
        route_to_agents,
        {
            "research": "research",
            "planning": "planning",
            "analysis": "analysis",
            "verification": "verification",
        },
    )

    for agent in ["research", "planning", "analysis", "verification"]:
        graph.add_conditional_edges(
            agent,
            next_agent,
            {
                "research": "research",
                "planning": "planning",
                "analysis": "analysis",
                "verification": "verification",
                "finish": END,
            },
        )

    return graph.compile()


def run_task(task: str) -> dict:
    workflow = build_graph()

    result = workflow.invoke({
        "task": task,
        "selected_agents": [],
        "results": [],
        "final_report": "",
    })

    report = "\n\n".join(
        f"### {item['agent']}\n{item['output']}"
        for item in result["results"]
    )

    return {
        "task": task,
        "selected_agents": result["selected_agents"],
        "results": result["results"],
        "final_report": report,
    }
