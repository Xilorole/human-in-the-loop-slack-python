"""MCP server implementation for human-in-the-loop interactions."""

import asyncio
from typing import Any, Dict, List, Sequence

from loguru import logger
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp import types

from .tools import HumanInterface, HumanTools


class HumanMCPServer:
    """MCP Server for human-in-the-loop interactions."""

    def __init__(self, human_interface: HumanInterface):
        self.human_interface = human_interface
        self.human_tools = HumanTools(human_interface)

        # Create MCP server
        self.server = Server("human-in-the-loop")

        # Register handlers
        self._register_handlers()

        logger.info("MCP server initialized")

    def _register_handlers(self) -> None:
        """Register MCP message handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Handle list_tools request."""
            logger.debug("Handling list_tools request")
            tools = self.human_tools.get_tools()
            return tools

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle call_tool request."""
            logger.debug(f"Handling call_tool request: {name}")
            try:
                content = await self.human_tools.call_tool(name, arguments)
                return content
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                error_content = [
                    types.TextContent(type="text", text=f"Error: {str(e)}")
                ]
                return error_content

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting MCP server...")

        # Use stdio transport
        import mcp.server.stdio

        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="Human-in-the-Loop MCP Server",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
