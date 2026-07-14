from langchain_core.messages import AIMessage, SystemMessage

from prompts import (
    BRAIN_SYSTEM_PROMPT,
    INTENT_EXTRACTION_PROMPT,
)

from utils.llm import (
    invoke_llm,
    extract_user_intent,
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


# -------------------------------------------------------
# Main Brain Node
# -------------------------------------------------------

def brain(state):

    messages = state["messages"]

    intent = extract_intent(messages)
    stage = state["conversation_stage"]

    if stage == "collecting_required_fields":

        if len(get_missing_fields(intent)) == 0:
            stage = "collecting_additional_context"

    elif stage == "collecting_additional_context":

        if intent.get("additional_context") is not None:
            stage = "ready_to_generate"

    # Always compute the workflow instruction AFTER updating the stage
    updated_state = {
        **state,
        "conversation_stage": stage,
    }

    workflow_instruction = get_workflow_instruction(
        updated_state,
        intent
    )

    reply = think(messages, workflow_instruction)
    if stage == "ready_to_generate":

      creative_result = run_creative_workflow(intent)

      print("\nCreative Workflow Result\n")
      print(creative_result)
    return {
    "messages": [reply],
    "user_intent": intent,
    "conversation_stage": stage,
}