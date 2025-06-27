"""Configuration management for the Human-in-the-Loop MCP server."""

import os
from dataclasses import dataclass
from typing import Optional

import click
from loguru import logger


@dataclass(frozen=True)
class Config:
    """Configuration for the Human-in-the-Loop MCP server."""
    
    slack_app_token: str
    slack_bot_token: str
    slack_channel_id: str
    slack_user_id: str
    log_level: str = "INFO"
    
    @classmethod
    def from_args(
        cls,
        slack_channel_id: str,
        slack_user_id: str,
        slack_app_token: Optional[str] = None,
        slack_bot_token: Optional[str] = None,
        log_level: str = "INFO",
    ) -> "Config":
        """Create config from command line arguments and environment variables."""
        
        # Get tokens from environment if not provided
        app_token = slack_app_token or os.getenv("SLACK_APP_TOKEN")
        bot_token = slack_bot_token or os.getenv("SLACK_BOT_TOKEN")
        
        if not app_token:
            raise click.ClickException(
                "SLACK_APP_TOKEN must be provided via environment variable"
            )
        
        if not bot_token:
            raise click.ClickException(
                "SLACK_BOT_TOKEN must be provided via environment variable"
            )
        
        config = cls(
            slack_app_token=app_token,
            slack_bot_token=bot_token,
            slack_channel_id=slack_channel_id,
            slack_user_id=slack_user_id,
            log_level=log_level,
        )
        
        logger.info("Configuration loaded successfully")
        return config


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level=level,
        colorize=True,
    )