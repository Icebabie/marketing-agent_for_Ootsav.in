from dotenv import load_dotenv
import os

load_dotenv()

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Higgsfield
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_SECRET = os.getenv("HF_API_SECRET")

# Image Generation Defaults
DEFAULT_IMAGE_MODEL = "bytedance/seedream/v4/text-to-image"
DEFAULT_IMAGE_RESOLUTION = "1K"