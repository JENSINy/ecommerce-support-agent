import uuid

from agents import Runner

from agent import (
    CustomerServiceContext,
    customer_service_agent,
)


def run_chat() -> None:
    session_id = str(uuid.uuid4())
    conversation = []

    print("电商售后 Agent 已启动")
    print(f"当前会话编号：{session_id}")
    print("输入 exit 结束对话")

    while True:
        user_input = input("\n用户：").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Agent：再见！")
            break

        if not user_input:
            continue

        conversation.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        try:
            result = Runner.run_sync(
                customer_service_agent,
                conversation,
                context=CustomerServiceContext(
                    session_id=session_id,
                ),
            )

            print(f"Agent：{result.final_output}")

            conversation = result.to_input_list()

        except Exception as error:
            print(f"Agent 运行失败：{error}")


if __name__ == "__main__":
    run_chat()
