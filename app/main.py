
from app.orchestrator import orchestrate_task


def main():
    print("=== Multi-Agent Task Automation System ===")

    user_task = input("\nEnter the task you want to automate: ").strip()

    if not user_task:
        print("Please enter a valid task.")
        return

    result = orchestrate_task(user_task)

    print("\n===== ORCHESTRATOR RESULT =====")
    print(f"Task: {result['task']}")
    print(f"Status: {result['status']}")
    print("\nAssigned agents:")

    for index, agent in enumerate(result["agents"], start=1):
        print(f"{index}. {agent}")


if __name__ == "__main__":
    main()
