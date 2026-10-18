
from app.graph_workflow import run_task


def main():
    print("=== Multi-Agent Task Automation System ===")

    task = input("\nEnter your task: ").strip()

    if not task:
        print("Please enter a valid task.")
        return

    print("\nStarting multi-agent workflow...")

    try:
        report = run_task(task)

        print("\n===== SELECTED AGENTS =====")
        for agent in report["selected_agents"]:
            print(f"- {agent.title()} Agent")

        print("\n===== FINAL EXECUTION REPORT =====")
        print(report["final_report"])

    except Exception as error:
        print(f"\nWorkflow failed: {error}")
        print("Check your API key, model availability, and network connection.")


if __name__ == "__main__":
    main()
