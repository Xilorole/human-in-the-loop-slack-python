"""MCP tools for human-in-the-loop interactions."""

from typing import Any, Dict, List, Protocol

from loguru import logger
from mcp import types
from pydantic import BaseModel, Field


class HumanInterface(Protocol):
    """Protocol for human interaction interface."""

    async def ask(self, question: str) -> str:
        """Ask a human a question and return their response."""
        ...


class AskHumanRequest(BaseModel):
    """Request model for ask_human tool."""

    question: str = Field(
        description="The question to ask the human. Be specific and provide context "
        "to help the human understand what information you need."
    )


class HumanTools:
    """Collection of human-in-the-loop tools."""

    def __init__(self, human_interface: HumanInterface):
        self.human_interface = human_interface
        logger.info("Human tools initialized")

    def get_tools(self) -> List[types.Tool]:
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

    async def call_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Call a tool with the given arguments."""
        logger.info(f"Calling tool: {name}")

        if name == "ask_human":
            return await self._ask_human(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def _ask_human(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle ask_human tool call."""
        try:
            # Validate request
            request = AskHumanRequest(**arguments)

            # Ask the human
            logger.info(f"Asking human: {request.question[:50]}...")
            response = await self.human_interface.ask(request.question)

            # Return response as text content
            return [types.TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error in ask_human tool: {e}")
            error_message = f"Error asking human: {str(e)}"
            return [types.TextContent(type="text", text=error_message)]
