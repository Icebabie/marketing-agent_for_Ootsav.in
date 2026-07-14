from graphs.creative_graph import creative_graph


def run_creative_workflow(user_intent: dict):
    return creative_graph.invoke(
        {
            "user_intent": user_intent,
            "final_prompt": "",
            "generated_images": []
        }
    )