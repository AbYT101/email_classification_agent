from typing import TypedDict, Literal


class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]


class EmailAgentState(TypedDict):
    email_content: str
    sender_email: str
    email_id: str

    classification: EmailClassification | None

    # Raw Search/API results
    search_result: list[str] | None
    customer_history: list[str] | None

    # Generate content
    draft_response: str | None
    messages: list[str] | None
