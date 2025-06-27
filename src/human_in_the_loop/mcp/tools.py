"""MCP tools for human-in-the-loop interactions."""

import json
from typing import Any, Protocol

from loguru import logger
from mcp import types
from pydantic import BaseModel, Field


class HumanInterface(Protocol):
    """Protocol for human interaction interface."""

    async def ask(self, question: str, thread_ts: str | None = None) -> tuple[str, str]:
        """Ask a human a question and return their response and thread_ts."""
        ...


class AskHumanRequest(BaseModel):
    """Request model for ask_human tool."""

    question: str = Field(
        description="The question to ask the human. Be specific and provide context "
        "to help the human understand what information you need."
    )
    thread_ts: str | None = Field(
        default=None,
        description=(
            "Slack thread timestamp to continue the conversation in the same thread. Leave blank to start a new thread."
        ),
    )


class HumanTools:
    """Collection of human-in-the-loop tools."""

    def __init__(self, human_interface: HumanInterface) -> None:
        """Initialize HumanTools with a human interface."""
        self.human_interface = human_interface
        logger.info("Human tools initialized")

    def get_tools(self) -> list[types.Tool]:
        """Get all available tools."""
        return [
            types.Tool(
                name="ask_human",
                description=(
                    "Ask a human for information that only they would know, such as "
                    "personal preferences, project-specific context, local environment "
                    "details, or non-public information"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": (
                                "The question to ask the human. Be specific and provide "
                                "context to help the human understand what information you need."
                            ),
                        }
                    },
                    "required": ["question"],
                },
            )
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        """Call a tool with the given arguments."""
        logger.info(f"Calling tool: {name}")

        if name == "ask_human":
            return await self._ask_human(arguments)
        msg = f"Unknown tool: {name}"
        raise ValueError(msg)

    async def _ask_human(self, arguments: dict[str, Any]) -> list[types.TextContent]:
        """Handle ask_human tool call."""
        try:
            # Validate request
            request = AskHumanRequest(**arguments)

            # Ask the human, get response and thread_ts
            logger.info(f"Asking human: {request.question[:50]}...")
            response, thread_ts = await self.human_interface.ask(request.question, request.thread_ts)

            # Return response and thread_ts as a JSON string in text
            return [types.TextContent(type="text", text=json.dumps({"response": response, "thread_ts": thread_ts}))]

        except (TypeError, ValueError) as e:
            logger.error(f"Error in ask_human tool: {e}")
            error_message = f"Error asking human: {e!s}"
            return [types.TextContent(type="text", text=error_message)]
