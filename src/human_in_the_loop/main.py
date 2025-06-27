"""Main entry point for the Human-in-the-Loop MCP server."""

import asyncio
import signal
import sys
from typing import Optional

import click
from loguru import logger

from .config import Config, setup_logging
from .mcp import HumanMCPServer
from .slack import HumanInterface, SlackClient


class GracefulExit(Exception):
    """Exception for graceful shutdown."""
    pass


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    raise GracefulExit()


async def run_server(config: Config) -> None:
    """Run the human-in-the-loop MCP server."""
    slack_client = None
    
    try:
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize Slack client
        slack_client = SlackClient(
            app_token=config.slack_app_token,
            bot_token=config.slack_bot_token,
            channel_id=config.slack_channel_id,
            user_id=config.slack_user_id,
        )
        
        # Create human interface
        human_interface = HumanInterface(slack_client)
        
        # Initialize MCP server
        mcp_server = HumanMCPServer(human_interface)
        
        # Start Slack client and MCP server concurrently
        logger.info("Starting services...")
        
        slack_task = asyncio.create_task(slack_client.start())
        
        # Give Slack a moment to connect
        await asyncio.sleep(2)
        
        # Start MCP server
        logger.info("Human-in-the-Loop MCP server is ready!")
        await mcp_server.run()
        
    except GracefulExit:
        logger.info("Graceful shutdown initiated")
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if slack_client:
            try:
                await slack_client.stop()
            except Exception as e:
                logger.error(f"Error stopping Slack client: {e}")
        
        logger.info("Shutdown complete")


@click.command()
@click.option(
    "--slack-channel-id",
    required=True,
    help="Slack channel ID where questions will be posted",
)
@click.option(
    "--slack-user-id",
    required=True,
    help="Slack user ID to mention when asking questions",
)
@click.option(
    "--slack-app-token",
    help="Slack app token (or set SLACK_APP_TOKEN environment variable)",
)
@click.option(
    "--slack-bot-token",
    help="Slack bot token (or set SLACK_BOT_TOKEN environment variable)",
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Log level",
)
def main(
    slack_channel_id: str,
    slack_user_id: str,
    slack_app_token: Optional[str] = None,
    slack_bot_token: Optional[str] = None,
    log_level: str = "INFO",
) -> None:
    """Human-in-the-Loop MCP Server for Slack.
    
    This server allows AI assistants to ask questions to humans via Slack.
    
    Required environment variables:
    - SLACK_APP_TOKEN: Your Slack app token
    - SLACK_BOT_TOKEN: Your Slack bot token
    
    Example usage:
    uv run human-in-the-loop --slack-channel-id C1234567890 --slack-user-id U0987654321
    """
    try:
        # Setup logging
        setup_logging(log_level)
        
        # Load configuration
        config = Config.from_args(
            slack_channel_id=slack_channel_id,
            slack_user_id=slack_user_id,
            slack_app_token=slack_app_token,
            slack_bot_token=slack_bot_token,
            log_level=log_level,
        )
        
        # Run the server
        asyncio.run(run_server(config))
        
    except click.ClickException as e:
        e.show()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()