from langchain_core.messages import HumanMessage, SystemMessage

from creative_director_prompts import CREATIVE_DIRECTOR_SYSTEM_PROMPT
from utils.llm import invoke_llm


def build_user_context(user_intent: dict) -> str:
    """
    Convert the structured user intent into a readable creative brief.
    """

    additional_context = user_intent.get("additional_context") or []

    if additional_context:
        additional_context = "\n".join(
            f"- {item}" for item in additional_context
        )
    else:
        additional_context = "None"

    return f"""
Campaign:
{user_intent.get("campaign")}

Content Type:
{user_intent.get("content_type")}

Language Style:
{user_intent.get("language_style")}

Design Preference:
{user_intent.get("design_preference")}

Additional Context:
{additional_context}
"""


def creative_director(state):

    print("\n🎨 Creative Director running...\n")

    creative_brief = build_user_context(
        state["user_intent"]
    )
    if state["edit_request"]:

        creative_brief += f"""

    This is an image editing request.

    Original Prompt:
    {state["final_prompt"]}

    Requested Changes:
    {state["edit_request"]}

    Keep everything else in the image unchanged unless required by the requested modification.
    """

    response = invoke_llm(
        [
            SystemMessage(
                content=CREATIVE_DIRECTOR_SYSTEM_PROMPT
            ),
            HumanMessage(content=creative_brief),
        ]
    )

    return {
        "final_prompt": response.text
    }