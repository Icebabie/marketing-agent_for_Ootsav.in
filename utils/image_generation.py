from pathlib import Path
from pprint import pprint

import higgsfield_client

from config import (
    DEFAULT_IMAGE_MODEL,
    DEFAULT_IMAGE_RESOLUTION,
)


def get_aspect_ratio(content_type: str) -> str:
    """
    Returns the appropriate aspect ratio based on the Instagram content type.
    """

    content_type = content_type.lower()

    if "story" in content_type:
        return "9:16"

    if "reel" in content_type:
        return "9:16"

    if "carousel" in content_type:
        return "4:5"

    # Default to portrait Instagram post
    return "4:5"


def generate_image(
    prompt: str,
    content_type: str,
    reference_images: list[str] | None = None,
):
    """
    Generate image(s) using the configured Higgsfield model.
    """

    if reference_images is None:
        reference_images = []

    aspect_ratio = get_aspect_ratio(content_type)

    print("\n==============================")
    print("🖼 IMAGE GENERATION")
    print("==============================")
    print(f"Model            : {DEFAULT_IMAGE_MODEL}")
    print(f"Aspect Ratio     : {aspect_ratio}")
    print(f"Resolution       : {DEFAULT_IMAGE_RESOLUTION}")
    print(f"Reference Images : {len(reference_images)}")
    print("==============================\n")

    uploaded_image_urls = []

    for image_path in reference_images:

        print(f"⬆️ Uploading: {image_path}")

        image_url = higgsfield_client.upload_file(
            Path(image_path)
        )

        uploaded_image_urls.append(image_url)

    arguments = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "quality": "low",
    }

    # Only include resolution if configured
    if DEFAULT_IMAGE_RESOLUTION:
        arguments["resolution"] = DEFAULT_IMAGE_RESOLUTION

    # Only include reference images if present
    if uploaded_image_urls:
        arguments["image_references"] = uploaded_image_urls

    print("📦 Generation Arguments")
    pprint(arguments)
    print()

    try:

        result = higgsfield_client.subscribe(
            DEFAULT_IMAGE_MODEL,
            arguments=arguments,
        )

        print("\n✅ Generation Successful\n")

        print("📄 Raw Response")
        pprint(result)
        print()

        # Temporary until we inspect the response structure.
        return result

    except Exception as e:

        print("\n❌ Image generation failed.\n")
        print(e)
        raise