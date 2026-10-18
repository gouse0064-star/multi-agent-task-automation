
from app.agents import (
    research_agent,
    planning_agent,
    analysis_agent,
    verification_agent,
    general_agent,
)


def assign_agents(user_task):
    task = user_task.lower()
    assignments = []

    if any(word in task for word in ["research", "find", "search", "investigate"]):
        assignments.append(research_agent)

    if any(word in task for word in ["plan", "roadmap", "prepare", "learn"]):
        assignments.append(planning_agent)

    if any(word in task for word in ["analyze", "analysis", "compare", "evaluate", "review"]):
        assignments.append(analysis_agent)

    if any(word in task for word in ["verify", "check", "validate"]):
        assignments.append(verification_agent)

    if not assignments:
        assignments.append(general_agent)

    return assignments


def orchestrate_task(user_task):
    selected_agents = assign_agents(user_task)
    results = []

    for agent in selected_agents:
        result = agent(user_task)
        results.append(result)

    return {
        "task": user_task,
        "status": "completed",
        "results": results,
    }
