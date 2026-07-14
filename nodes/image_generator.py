from utils.image_generation import generate_image


def image_generator(state):

    print("\n🖼 Image Generator running...\n")

    result = generate_image(
        prompt=state["final_prompt"],
        content_type=state["user_intent"]["content_type"],
        reference_images=state.get("reference_images", []),
    )

    return {
        "generated_images": result
    }