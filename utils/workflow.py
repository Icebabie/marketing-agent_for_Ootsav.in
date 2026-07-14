FIELD_REGISTRY = {
    "campaign": {
        "instruction": "Ask the user what campaign, feature, or idea they want to promote."
    },
    "content_type": {
        "instruction": "Ask whether they want a post, reel, story, or carousel."
    },
    "language_style": {
        "instruction": "Ask what writing style they want. For example, Ootsav's usual Hinglish, plain English, professional, casual, etc."
    },
    "design_preference": {
        "instruction": "Ask about any design preferences like colors, illustrations, realism, typography, layout, mood, or reference style."
    }
}

REQUIRED_FIELDS = list(FIELD_REGISTRY.keys())

def get_missing_fields(user_intent: dict) -> list[str]:
    """
    Return all required fields that are still missing.
    """

    missing = []

    for field in REQUIRED_FIELDS:

        if not user_intent.get(field):
            missing.append(field)

    return missing

def get_next_missing_field(user_intent: dict) -> dict | None:
    """
    Return information about the next field that needs to be collected.
    """

    missing = get_missing_fields(user_intent)

    if not missing:
        return None

    field = missing[0]

    return {
        "field": field,
        "instruction": FIELD_REGISTRY[field]["instruction"]
    }

def is_ready_to_generate(user_intent: dict) -> bool:
    """
    Check whether we have collected all required information.
    """

    return len(get_missing_fields(user_intent)) == 0

def get_workflow_instruction(state, user_intent):

    stage = state["conversation_stage"]

    # Stage 1
    if stage == "collecting_required_fields":

        missing = get_missing_fields(user_intent)

        if missing:

            field = missing[0]

            return {
                "stage": stage,
                "field": field,
                "instruction": FIELD_REGISTRY[field]["instruction"]
            }

        return {
            "stage": "collecting_additional_context"
        }

    # Stage 2
    elif stage == "collecting_additional_context":

        return {
            "stage": stage
        }

    # Stage 3
    elif stage == "ready_to_generate":

        return {
            "stage": stage
        }