
from app.graph_workflow import run_task


def main():
    print("=== LangGraph AI Task System ===")

    task = input("\nEnter your task: ").strip()

    if not task:
        print("Please enter a valid task.")
        return

    print("\nProcessing your task...")

    result = run_task(task)

    print("\n===== AI GENERATED RESPONSE =====")
    print(result["response"])


if __name__ == "__main__":
    main()
