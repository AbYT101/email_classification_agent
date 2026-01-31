# Email Classification Agent

An intelligent email processing system that automatically classifies emails, searches documentation, tracks bugs, drafts responses, and routes emails for human review.

## Features

- **Email Classification**: Automatically categorizes incoming emails by intent
- **Documentation Search**: Searches relevant documentation for responses
- **Bug Tracking**: Routes emails to bug tracking systems when needed
- **Response Drafting**: Generates appropriate email responses
- **Human Review**: Includes human-in-the-loop approval before sending

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
python main.py
```

## Architecture

The system uses LangGraph to orchestrate a multi-step workflow:

1. Read Email
2. Classify Intent
3. Branch to: Search Documentation or Bug Tracking
4. Draft Response
5. Human Review
6. Send Reply

## Dependencies

- `langchain` >= 1.2.7
- `langchain-ollama` >= 1.0.1
