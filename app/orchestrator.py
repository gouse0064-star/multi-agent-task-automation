
def assign_agents(user_task):
    """Assign specialized agents based on the user's task."""

    task = user_task.lower()
    assignments = []

    if any(word in task for word in ["research", "find", "search", "investigate"]):
        assignments.append("Research Agent")

    if any(word in task for word in ["plan", "roadmap", "prepare", "learn"]):
        assignments.append("Planning Agent")

    if any(word in task for word in ["analyze", "compare", "evaluate", "review"]):
        assignments.append("Analysis Agent")

    if any(word in task for word in ["verify", "check", "validate"]):
        assignments.append("Verification Agent")

    # Every task should have at least one assigned agent.
    if not assignments:
        assignments.append("General Assistant Agent")

    return assignments


def orchestrate_task(user_task):
    """Create a task plan and assign agents to it."""

    agents = assign_agents(user_task)

    return {
        "task": user_task,
        "agents": agents,
        "status": "planned",
    }
