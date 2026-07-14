from dotenv import load_dotenv
import os

load_dotenv()

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Higgsfield
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_SECRET = os.getenv("HF_API_SECRET")

# Image Generation Defaults
DEFAULT_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "higgsfield-ai/soul/standard")
DEFAULT_IMAGE_RESOLUTION = os.getenv("HF_IMAGE_RESOLUTION", "720p")