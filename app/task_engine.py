
def create_task_plan(user_task):
    """Break a user request into a basic execution plan."""

    steps = [
        "Understand the user's objective",
        "Identify the information and tools required",
        "Execute the required subtasks",
        "Verify the results",
        "Prepare the final response",
    ]

    return {
        "task": user_task,
        "status": "planned",
        "steps": steps,
    }


def display_task_plan(plan):
    print("\n===== TASK EXECUTION PLAN =====")
    print(f"Task: {plan['task']}")
    print(f"Status: {plan['status']}")
    print("\nExecution steps:")

    for index, step in enumerate(plan["steps"], start=1):
        print(f"{index}. {step}")
