from app.task_engine import create_task_plan, display_task_plan


def main():
    print("=== Multi-Agent Task Automation System ===")

    user_task = input("\nEnter the task you want to automate: ").strip()

    if not user_task:
        print("Please enter a valid task.")
        return

    plan = create_task_plan(user_task)
    display_task_plan(plan)


if __name__ == "__main__":
    main()
