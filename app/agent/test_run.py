from app.config import get_settings

from app.agent.orchestrator import run_agent

def main():
    result = run_agent(
        user_message="How is Nvidia doing?",
        history=[],
        settings=get_settings()
    )

    print(result)

if __name__ == "__main__":
    main()