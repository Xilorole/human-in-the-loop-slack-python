"""Utilities for formatting Slack messages with Block Kit."""

# Use built-in types and new union syntax per PEP 585/604
from loguru import logger

MAX_THREAD_TITLE_LENGTH = 100  # Named constant for magic value


def format_question_blocks(
    question: str,
    user_id: str | None = None,
    thread_title: str | None = None,
) -> list[dict]:
    """Format a question using Slack Block Kit with improved structure and clarity.

    Args:
        question: The question text to format
        user_id: Optional user ID to mention
        thread_title: Optional thread title (defaults to first part of question)

    Returns:
        List of Block Kit blocks

    """
    # If thread_title not provided, use first part of question
    if not thread_title:
        thread_title = question[:MAX_THREAD_TITLE_LENGTH].strip()
        if len(question) > MAX_THREAD_TITLE_LENGTH:
            thread_title += "..."

    blocks = [
        # Header section
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":robot_face: Question from AI Assistant",
                "emoji": True,
            },
        },
        {"type": "divider"},
        # Context section with icon and info
        {
            "type": "context",
            "elements": [
                {
                    "type": "image",
                    "image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
                    "alt_text": "AI Question",
                },
                {"type": "mrkdwn", "text": "*Human input requested*"},
            ],
        },
        {"type": "divider"},
        # Thread title as bolded section (Slack mrkdwn uses single asterisks)
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Thread:* {thread_title}"},
        },
        # Question text as section with mrkdwn
        {"type": "section", "text": {"type": "mrkdwn", "text": question}},
    ]

    # Add user mention if provided
    if user_id:
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Please respond, <@{user_id}>:*"},
            }
        )

    blocks.append({"type": "divider"})
    return blocks


def format_thread_initial_message(thread_title: str) -> list[dict]:
    """Format the initial thread message using Block Kit with improved clarity.

    Args:
        thread_title: Short title for the thread

    Returns:
        List of Block Kit blocks

    """
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":robot_face: Question from AI Assistant",
                "emoji": True,
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Thread:* {thread_title}"},
        },
    ]


def plain_text_to_mrkdwn(text: str) -> str:
    """Convert plain text to Slack mrkdwn format.

    This handles basic formatting like preserving code blocks and paragraphs.

    Args:
        text: Plain text to convert

    Returns:
        Text formatted for Slack's mrkdwn

    """
    try:
        # Replace code blocks
        # This is a simple implementation, a more robust one would handle
        # nested code blocks and other edge cases
        lines = text.split("\n")
        formatted_lines = []
        in_code_block = False

        for line in lines:
            # Handle code blocks with triple backticks
            if line.strip().startswith("```") or line.strip().endswith("```"):
                in_code_block = not in_code_block
                formatted_lines.append(line)
            elif in_code_block:
                # Don't format code inside blocks
                formatted_lines.append(line)
            else:
                # Format inline code with single backticks (leave them as is)
                # Add any other formatting rules here if needed
                formatted_lines.append(line)

        return "\n".join(formatted_lines)
    except (ValueError, AttributeError) as e:
        logger.error(f"Error formatting markdown: {e}")
        return text  # Return original text if formatting fails
