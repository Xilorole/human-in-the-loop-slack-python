"""Utilities for formatting Slack messages with Block Kit."""

from typing import Dict, List, Optional

from loguru import logger


def format_question_blocks(
    question: str, 
    user_id: Optional[str] = None,
    thread_title: Optional[str] = None,
) -> List[Dict]:
    """Format a question using Slack Block Kit.
    
    Args:
        question: The question text to format
        user_id: Optional user ID to mention
        thread_title: Optional thread title (defaults to first part of question)
    
    Returns:
        List of Block Kit blocks
    """
    # If thread_title not provided, use first part of question
    if not thread_title:
        thread_title = question[:100].strip()
        if len(question) > 100:
            thread_title += "..."
    
    blocks = [
        # Header section
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Question from AI Assistant",
                "emoji": True
            }
        },
        
        # Context section with icon
        {
            "type": "context",
            "elements": [
                {
                    "type": "image",
                    "image_url": "https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
                    "alt_text": "AI Question"
                },
                {
                    "type": "mrkdwn",
                    "text": "Human input requested"
                }
            ]
        },
        
        # Divider
        {"type": "divider"},
        
        # Question text as section with markdown
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": question
            }
        }
    ]
    
    # Add user mention if provided
    if user_id:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Please respond, <@{user_id}>:*"
            }
        })
    
    return blocks


def format_thread_initial_message(thread_title: str) -> List[Dict]:
    """Format the initial thread message using Block Kit.
    
    Args:
        thread_title: Short title for the thread
        
    Returns:
        List of Block Kit blocks
    """
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🤖 *Question from AI Assistant*\n{thread_title}"
            }
        }
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
    except Exception as e:
        logger.error(f"Error formatting markdown: {e}")
        return text  # Return original text if formatting fails
