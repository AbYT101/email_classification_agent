from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy
from langgraph.graph import StateGraph, END, START
from nodes.response_nodes import draft_response, human_review, send_reply
from state.state import EmailAgentState, EmailClassification
from nodes.read_and_classify_nodes import read_email, classify_intent
from nodes.searching_and_tracking_nodes import bug_tracking, search_documentation


workflow = StateGraph(EmailAgentState)
workflow.add_node("read_email", read_email)
workflow.add_node("classify_intent", classify_intent)


workflow.add_node(
    "search_documentation",
    search_documentation,
    retry_policy=RetryPolicy(max_attempts=3),
)
workflow.add_node("bug_tracking", bug_tracking)
workflow.add_node("draft_response", draft_response)
workflow.add_node("human_review", human_review)
workflow.add_node("send_reply", send_reply)

workflow.add_edge(START, "read_email")
workflow.add_edge("read_email", "classify_intent")
workflow.add_edge("send_reply", END)

memory = MemorySaver()

app = workflow.compile(checkpointer=memory)


def main():
    print("Hello from email-classification-agent!")
    initial_state = {
        "email_content": "I was charged twice for my subscription! This is urgent!",
        "sender_email": "customer@example.com",
        "email_id": "email_123",
        "messages": [],
    }
    
    config = {"configurable": {"thread_id": "customer_123"}}
    
    result = app.invoke(initial_state, config)
    
    print(f"human review interrupt: {result['__interrupt__']}")
    
    from langgraph.types import Command
    
    human_response = Command(
        resume = {
            "approved": True,
            "edited_response": "We sincerely apologize for the double charge. I've initiated an immediate refund..."
        }
    )
    
    final_result = app.invoke(human_response, config)
    
    print(f"Email sent successfully")


if __name__ == "__main__":
    main()
