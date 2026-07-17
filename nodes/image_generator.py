from utils.image_generation import generate_image


def image_generator(state):
    try:
        print("\n🖼 Image Generator running...\n")

        result = generate_image(
            prompt=state["final_prompt"],
            content_type=state["user_intent"]["content_type"],
            reference_images=state.get("reference_images", []),
        )

        return {
            "generated_images": result
        }
    except Exception as e:
        print(f"Error occurred while generating image: {e}")
        return {
            "generated_images": [],
            "generation_error": str(e)
        }