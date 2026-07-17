from langchain_core.messages import HumanMessage

from graphs.conversation_graph import graph


def main():
    print("=" * 60)
    print("Ootsav AI Marketing Agent for IG")
    print("=" * 60)
    print("\nType 'exit' anytime to quit.\n")

    state = {
        "messages": [],
        "user_intent": {},
        "conversation_stage": "collecting_required_fields",

        "final_prompt": "",
        "generated_images": [],
        "reference_images": [],
    }

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("\n Goodbye!")
            break

        state["messages"].append(
            HumanMessage(content=user_input)
        )

        state = graph.invoke(state)

        ai_message = state["messages"][-1]

        print(f"\n🤖 Brain:\n{ai_message.content}\n")

        generated_images = state.get("generated_images", [])

        if generated_images:

            print("=" * 60)
            print("🖼 Generated Images")
            print("=" * 60)

            for index, image in enumerate(generated_images, start=1):
                print(f"{index}. {image}")

            print("=" * 60)
        
        print("\n" + "=" * 60)
        print("Conversation Stage")
        print("=" * 60)
        print(state["conversation_stage"])

        print("\nCurrent Intent")
        print("=" * 60)
        print(state["user_intent"])
        print("=" * 60 + "\n")



if __name__ == "__main__":
    main()