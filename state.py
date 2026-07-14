from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]

    user_intent: dict

    conversation_stage: str

class CreativeState(TypedDict):
    user_intent: dict

    final_prompt: str

    generated_images: list