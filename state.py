from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class State(TypedDict):
    # Conversation
    messages: Annotated[list, add_messages]

    # User requirements
    user_intent: dict

    # Workflow stage
    conversation_stage: str

    # Creative outputs
    final_prompt: str

    generated_images: list[str]

    reference_images: list[str]


class CreativeState(TypedDict):
    user_intent: dict

    final_prompt: str

    generated_images: list[str]

    reference_images: list[str]

    edit_request: str | None

    generation_error: str | None