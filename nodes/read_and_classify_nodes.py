from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain.messages import HumanMessage
from state.state import EmailAgentState, EmailClassification
from llm.llm import llm


def read_email(state: EmailAgentState):
    """Extract and parse email content"""
    # In prod it should be from an email server
    return {
        "messages": [
            HumanMessage(content=f"Processing email: {state['email_content']}")
        ]
    }


def classify_intent(
    state: EmailAgentState,
) -> Command[
    Literal["search_documentation", "human_review", "draft_response", "bug_tracking"]
]:
    """Use LLM to classify email intent and urgency, then route accordingly"""
    # Let's use LLM to classify the intent and urgency and rout to right node accordingly

    structured_llm = llm.with_structured_output(EmailClassification)

    classification_prompt = f"""
        Analyze this customer email and classify it:
        
        Email: {state['email_content']}
        From:  {state['sender_email']}
        
        Provide classification including intent, urgency, topic and summary.
    """

    classification = structured_llm.invoke(classification_prompt)

    if classification["intent"] == "billing" or classification["urgency"] == "critical":
        goto = "human_review"

    elif classification["intent"] in ["question", "feature"]:
        goto = "search_documentation"

    elif classification["intent"] == "bug":
        goto = "bug_tracking"
    else:
        goto = "draft_response"

    return Command(update={"classification": classification}, goto=goto)
