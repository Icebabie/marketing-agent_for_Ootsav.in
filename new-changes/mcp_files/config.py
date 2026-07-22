#config.py

from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Higgsfield (legacy REST API key/secret) -------------------------------
# No longer used for image generation — Higgsfield blocks external models
# on the plain API-key endpoint. Kept only in case you still need it for
# something outside generation (e.g. an old upload call). Safe to delete
# once you've confirmed nothing else references these.
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_SECRET = os.getenv("HF_API_SECRET")

# --- Higgsfield (MCP) --------------------------------------------------
# Hosted MCP server. Override via .env if Higgsfield changes the URL or
# you point at a self-hosted MCP server instead.
HIGGSFIELD_MCP_URL = os.getenv("HIGGSFIELD_MCP_URL", "https://mcp.higgsfield.ai/mcp")

# Where OAuth tokens + client registration info get cached on disk so the
# app doesn't need to open a browser on every run. Override via .env if
# you want it somewhere else (e.g. inside the project for a dev container).
HIGGSFIELD_TOKEN_STORE_PATH = Path(
    os.getenv(
        "HIGGSFIELD_TOKEN_STORE_PATH",
        str(Path.home() / ".config" / "ootsav-ads" / "higgsfield_tokens.json"),
    )
)

# Image Generation Defaults
DEFAULT_IMAGE_MODEL = "gpt_image_2"
DEFAULT_IMAGE_RESOLUTION = "1k"
