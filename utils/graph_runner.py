from graphs.creative_graph import creative_graph


def run_creative_workflow(
    user_intent: dict,
    reference_images: list[str] | None = None,
    edit_request: str | None = None,
    final_prompt: str = "",
):
    if reference_images is None:
        reference_images = []
    initial_state = {
        "user_intent": user_intent,
        "final_prompt": final_prompt,
        "generated_images": [],
        "reference_images": reference_images,
        "edit_request": edit_request,
    }

    return creative_graph.invoke(initial_state)