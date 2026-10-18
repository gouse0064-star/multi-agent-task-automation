
def research_agent(task):
    """Prepare research actions for a given task."""
    return {
        "agent": "Research Agent",
        "task": task,
        "result": (
            "Identify reliable sources, gather relevant information, "
            "and summarize the findings."
        ),
        "status": "completed",
    }


def planning_agent(task):
    """Create actionable steps for a given task."""
    return {
        "agent": "Planning Agent",
        "task": task,
        "result": [
            "Define the objective",
            "Break the objective into smaller steps",
            "Prioritize the steps",
            "Define the expected outcome",
        ],
        "status": "completed",
    }


def analysis_agent(task):
    """Prepare an analysis of a given task."""
    return {
        "agent": "Analysis Agent",
        "task": task,
        "result": (
            "Identify relevant factors, compare alternatives, "
            "and evaluate the findings."
        ),
        "status": "completed",
    }


def verification_agent(task):
    """Define verification checks for a given task."""
    return {
        "agent": "Verification Agent",
        "task": task,
        "result": [
            "Check completeness",
            "Check consistency",
            "Identify missing information",
        ],
        "status": "completed",
    }


def general_agent(task):
    """Handle tasks that do not match a specialized agent."""
    return {
        "agent": "General Assistant Agent",
        "task": task,
        "result": "Clarify the objective and identify the next actions.",
        "status": "completed",
    }
