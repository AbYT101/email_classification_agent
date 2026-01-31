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


def search_documentation(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """Search knowledge base for relevant information"""

    classification = state.get("classification", {})
    query = f"{classification.get("intent", "")} {classification.get("topic", "")}"

    try:
        search_results = [
            "Reset password via Settings > Security > Change Password",
            "Password must be at least 12 characters",
            "Include uppercase, lowercase, numbers, and symbols",
        ]

    except SearchAPIError as e:
        # For recoverable search errors, store error and continue
        search_results = [f"Search temporarily unavailable: {str(e)}"]

    return Command(update={"search_results": search_results}, goto="draft_response")


def bug_tracking(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """Create or update bug tracking ticket"""
    # Create ticket in your bug tracking system
    ticket_id = "BUG-12345"

    return Command(
        update={
            "search_results": [f"Bug tickets {ticket_id} created"],
            "current_step": "bug_tracked",
        },
        goto="draft_response",
    )



