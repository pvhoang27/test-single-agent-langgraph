from uuid import uuid4

from langchain_core.messages import HumanMessage

from app.graph import graph
from app.tools import initialize_database


def main() -> None:
    initialize_database()
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("Expense Agent đã sẵn sàng. Gõ 'exit' để thoát.")
    while True:
        try:
            user_input = input("\nBạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nTạm biệt!")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Tạm biệt!")
            break
        if not user_input:
            continue

        result = graph.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )
        print(f"Agent: {result['messages'][-1].content}")


if __name__ == "__main__":
    main()
