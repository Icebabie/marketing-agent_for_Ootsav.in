from langchain_core.messages import AIMessage, SystemMessage

from prompts import (
    BRAIN_SYSTEM_PROMPT,
    INTENT_EXTRACTION_PROMPT,
    REVIEW_INTENT_PROMPT,
)


import state
from utils.llm import (
    invoke_llm,
    extract_user_intent,
    extract_review_intent,
)

from utils.workflow import (
    get_missing_fields,
    is_ready_to_generate,
    get_workflow_instruction
)
from utils.graph_runner import run_creative_workflow

# -------------------------------------------------------
# Intent Extraction
# -------------------------------------------------------

def extract_intent(messages):
    """
    Extract structured user intent from the conversation.
    """

    response = extract_user_intent(
        [SystemMessage(content=INTENT_EXTRACTION_PROMPT)] + messages
    )

    return response.model_dump()


def classify_review(messages):
    """
    Classify what the user wants to do after
    an image has been generated.
    """

    response = extract_review_intent(
        [
            SystemMessage(content=REVIEW_INTENT_PROMPT),
            messages[-1],
        ]
    )

    return response


def update_conversation_stage(current_stage: str, intent: dict) -> str:
    """
    Determine the next conversation stage based on the
    current stage and the extracted user intent.
    """

    if current_stage == "collecting_required_fields":

        if len(get_missing_fields(intent)) == 0:
            return "collecting_additional_context"

        return current_stage

    if current_stage == "collecting_additional_context":

        if intent.get("additional_context") is not None:
            return "ready_to_generate"

        return current_stage

    return current_stage



# -------------------------------------------------------
# Brain Response Generation
# -------------------------------------------------------

def build_system_messages(workflow_instruction):
    """
    Build the system messages that guide the Brain.
    """

    system_messages = [BRAIN_SYSTEM_PROMPT]

    stage = workflow_instruction["stage"]

    if stage == "collecting_required_fields":

      system_messages.append(
          SystemMessage(
              content=f"""
                The only missing information is:

                {workflow_instruction["field"]}

                Instruction:

                {workflow_instruction["instruction"]}

                Ask exactly ONE natural follow-up question.

                Do not ask about anything else.
                """
          )
      )
    elif stage == "collecting_additional_context":

      system_messages.append(
          SystemMessage(
              content="""
              All required information has been collected.

              Ask ONE final question.

              Ask if the user has any additional ideas,
              references,
              creative inspirations,
              or anything else they would like the Creative Director to know.

              If they say "No", accept it and do not ask anything further.
              """
          )
      )

    elif stage == "ready_to_generate":

      system_messages.append(
          SystemMessage(
              content="""
              All information has been collected.

              Do NOT ask any more questions.

              Tell the user you're starting the creative generation process.

              Do NOT generate prompts or content yourself.
              """
          )
      )  
    return system_messages


def think(messages, workflow_instruction):
    """
    Generate the Brain's conversational reply.
    """

    response = invoke_llm(
        build_system_messages(workflow_instruction) + messages
    )

    return AIMessage(content=response.text)



def handle_collection(
    messages,
    intent,
    stage,
    workflow_instruction,
):
    """
    Handle the normal conversational data collection flow.
    """

    reply = think(
        messages,
        workflow_instruction,
    )

    return {
        "messages": [reply],
        "user_intent": intent,
        "conversation_stage": stage,
    }



def handle_generation(intent):
    """
    Run the Creative Graph and prepare the state
    for image review.
    """

    creative_result = run_creative_workflow(
        user_intent=intent,
    )

    if creative_result.get("generation_error"):

        reply = AIMessage(
            content=(
                "Sorry, I couldn't generate the image this time.\n\n"
                "Please try again in a moment."
            )
        )

        return {
            **state,
            "messages": [reply],
        }

    print("\nCreative Workflow Result\n")
    print(creative_result)

    reply = AIMessage(
        content=(
            "Your creative has been generated successfully!\n\n"
            "Take a look at it and let me know if you'd like to make any changes."
        )
    )

    return {
        "messages": [reply],
        "user_intent": intent,
        "conversation_stage": "reviewing_image",

        "generated_images": creative_result["generated_images"],
        "final_prompt": creative_result["final_prompt"],
    }


def handle_review(state):
    """
    Handle the image review stage.
    """

    review = classify_review(state["messages"])

    print("\nReview Intent\n")
    print(review)

    if review.action == "accept":

        reply = AIMessage(
            content=(
                "Awesome! 🎉\n\n"
                "I'm glad you liked it.\n"
                "You can now download the image.\n\n"
                "Whenever you're ready, we can also start a brand new creative."
            )
        )

        return {
            **state,
            "messages": [reply],
        }

    if review.action == "restart":

        reply = AIMessage(
            content=(
                "Sounds good! Let's start fresh.\n\n"
                "What would you like to create today?"
            )
        )

        return {
            "messages": [reply],
            "user_intent": {},
            "conversation_stage": "collecting_required_fields",
            "final_prompt": "",
            "generated_images": [],
            "reference_images": [],
        }

    if review.action == "edit":

        creative_result = run_creative_workflow(
            user_intent=state["user_intent"],
            reference_images=state["generated_images"],
            edit_request=review.edit_request,
            final_prompt=state["final_prompt"],
        )

        reply = AIMessage(
            content=(
                "I've updated the image based on your feedback.\n\n"
                "Take a look and let me know if you'd like to make any more changes."
            )
        )

        return {
            **state,
            "messages": [reply],
            "generated_images": creative_result["generated_images"],
            "final_prompt": creative_result["final_prompt"],
        }


# -------------------------------------------------------
# Main Brain Node
# -------------------------------------------------------

def brain(state):

    messages = state["messages"]

    intent = extract_intent(messages)

    stage = update_conversation_stage(
        state["conversation_stage"],
        intent,
    )

    workflow_instruction = get_workflow_instruction(
        {
            **state,
            "conversation_stage": stage,
        },
        intent,
    )

    if stage == "ready_to_generate":
        return handle_generation(intent)

    if stage == "reviewing_image":
        return handle_review(state)

    return handle_collection(
        messages,
        intent,
        stage,
        workflow_instruction,
    )