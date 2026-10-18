
from app.orchestrator import orchestrate_task


def main():
    print("=== Multi-Agent Task Automation System ===")

    user_task = input("\nEnter the task you want to automate: ").strip()

    if not user_task:
        print("Please enter a valid task.")
        return

    report = orchestrate_task(user_task)

    print("\n===== EXECUTION REPORT =====")
    print(f"Task: {report['task']}")
    print(f"Status: {report['status']}")

    for result in report["results"]:
        print(f"\n--- {result['agent']} ---")
        print(f"Result: {result['result']}")


if __name__ == "__main__":
    main()
