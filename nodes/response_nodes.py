from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command, RetryPolicy
from langchain_ollama import ChatOllama
from langchain.messages import HumanMessage
from state.state import EmailAgentState, EmailClassification
from llm.llm import llm


class SearchAPIError(Exception):
    """Exception raised when search API fails"""

    pass


def draft_response(
    state: EmailAgentState,
) -> Command[Literal["human_review", "send_reply"]]:
    """Generate response using context and route based on quality"""
    classification = state.get("classification", {})

    context_section = []

    if state.get("search_result"):
        formatted_docs = "\n".join([f"- {doc}" for doc in state["search_result"]])
        context_section.append(f"Relevant documentation: \n{formatted_docs}")

    if state.get("customer_history"):
        context_section.append(
            f"Customer tier: {state['customer_history'].get('tier', 'standard')}"
        )

    draft_prompt = f"""
        Draft a response to this customer email:
        {state['email_content']}

        Email intent: {classification.get('intent', 'unknown')}
        Urgency level: {classification.get('urgency', 'medium')}

        {chr(10).join(context_section)}

        Guidelines:
        - Be professional and helpful
        - Address their specific concern
        - Use the provided documentation when relevant
        """

    response = llm.invoke(draft_prompt)

    need_review = (
        classification.get("urgency") in ["high", "critical"]
        or classification.get("intent") == "complex"
    )

    goto = "human_review" if need_review else "send_reply"

    return Command(update={"draft_response": response.content}, goto=goto)


def human_review(state: EmailAgentState) -> Command[Literal["send_reply", END]]:
    """Pause for human review using interrupt and route based on decision"""

    classification = state.get("classification", {})

    human_decision = interrupt(
        {
            "email_id": state.get("email_id", ""),
            "original_email": state.get("email_content", ""),
            "draft_email": state.get("draft_response", ""),
            "urgency": classification.get("urgency"),
            "intent": classification.get("intent"),
            "action": "Please review and approve/edit this response",
        }
    )

    if human_decision.get("approved"):
        return Command(
            update={
                "draft_response": human_decision.get(
                    "edited_response", state.get("draft_response", "")
                )
            },
            goto="send_reply",
        )


def send_reply(state: EmailAgentState) -> dict:
    print(f"Sending a reply: {state['draft_response'][:100]}...")
    return {}
