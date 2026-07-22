#utils/image_generation.py

import asyncio
from pprint import pprint

from utils.higgsfield_mcp_client import higgsfield_mcp

from config import (
    DEFAULT_IMAGE_MODEL,
    DEFAULT_IMAGE_RESOLUTION,
)

# Tool name as exposed by the hosted Higgsfield MCP server. Confirm this
# (and the argument names in `arguments` below) against the real tool
# list first — run: python -m utils.higgsfield_mcp_client
GENERATE_IMAGE_TOOL = "generate_image"


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


async def _generate_image_async(
    prompt: str,
    content_type: str,
    reference_images: list[str] | None = None,
):
    """
    Generate image(s) via the Higgsfield MCP server.
    """

    if reference_images is None:
        reference_images = []

    aspect_ratio = get_aspect_ratio(content_type)

    print("\n==============================")
    print("🖼 IMAGE GENERATION (Higgsfield MCP)")
    print("==============================")
    print(f"Model            : {DEFAULT_IMAGE_MODEL}")
    print(f"Aspect Ratio     : {aspect_ratio}")
    print(f"Resolution       : {DEFAULT_IMAGE_RESOLUTION}")
    print(f"Reference Images : {len(reference_images)}")
    print("==============================\n")

    # IMPORTANT — unresolved piece, please verify before relying on this:
    # The MCP generate_image tool takes reference images as public URLs
    # (e.g. "reference_images": ["https://.../image.jpg"]), not local file
    # paths and not raw bytes. Your old code uploaded local files via
    # higgsfield_client.upload_file() to get a URL first — that upload
    # call went through the same REST API that's now blocked for external
    # models, so it may or may not still work for a plain file upload
    # (as opposed to generation). Two options:
    #   1. Check `higgsfield_mcp.list_tools()` for an upload-style tool
    #      (e.g. "upload_image") and call that instead.
    #   2. Host the local files yourself (S3, your own server, etc.) and
    #      pass those URLs in here.
    # For now this assumes `reference_images` already contains usable URLs.
    # A generated image you want to feed back in for editing (per your
    # "use the generated image again" workflow) already comes back from
    # Higgsfield as a hosted URL, so that specific case needs no upload
    # step at all — just pass the URL straight back in here.
    image_reference_urls = reference_images

    arguments = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "model": DEFAULT_IMAGE_MODEL,
    }

    if DEFAULT_IMAGE_RESOLUTION:
        arguments["resolution"] = DEFAULT_IMAGE_RESOLUTION

    if image_reference_urls:
        arguments["reference_images"] = image_reference_urls

    print("📦 Generation Arguments")
    pprint(arguments)
    print()

    try:
        result = await higgsfield_mcp.call_tool(GENERATE_IMAGE_TOOL, arguments)

        print("\n✅ Generation Successful\n")
        print("📄 Raw Response")
        pprint(result)
        print()

        return result

    except Exception as e:
        print("\n❌ Image generation failed.\n")
        print(e)
        raise


def generate_image(
    prompt: str,
    content_type: str,
    reference_images: list[str] | None = None,
):
    """
    Sync wrapper around the async MCP call, so existing LangGraph nodes
    (which call this synchronously) don't need to change.
    """

    return asyncio.run(
        _generate_image_async(prompt, content_type, reference_images)
    )
