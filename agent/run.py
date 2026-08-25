from langchain_core.messages import HumanMessage
from .agent import ChatEPCIS

def main():
    """
    ChatEPCIS Agent를 생성하고 터미널에서 대화를 수행합니다.
    """
    chat_epcis=ChatEPCIS(
        model_name="gemma4",
        ollama_port=11434
    )
    agent=chat_epcis.get_agent()
    messages=[]

    print("ChatEPCIS Agent가 실행되었습니다.")
    print("종료하려면 exit 또는 quit를 입력하세요.\n")
    while True:
        try:
            user_input=input("User: ").strip()

            if not user_input:
                continue

            if user_input.lower() in {
                "exit",
                "quit",
            }:
                print("ChatEPCIS Agent를 종료합니다.")
                break

            messages.append(
                HumanMessage(
                    content=user_input,
                )
            )

            result=agent.invoke(
                {
                    "messages": messages,
                }
            )
            messages=result["messages"]
            response=messages[-1]
            print(f"ChatEPCIS Agent: {response.content}\n")

        except KeyboardInterrupt:
            print("\nChatEPCIS Agent를 종료합니다.")
            break

        except Exception as e:
            print(f"Agent 실행 중 오류가 발생했습니다: {e}\n")

if __name__=="__main__":
    main()
