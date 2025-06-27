"""Slack client for human-in-the-loop communication."""

import asyncio
from typing import Dict, Set

from loguru import logger
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient


class SlackClient:
    """Handles Slack communication for human-in-the-loop interactions."""

    def __init__(self, app_token: str, bot_token: str, channel_id: str, user_id: str):
        self.channel_id = channel_id
        self.user_id = user_id
        self.app = AsyncApp(token=bot_token)
        self.handler = AsyncSocketModeHandler(self.app, app_token)
        self.client = AsyncWebClient(token=bot_token)

        # Track active conversations
        self._pending_responses: Dict[str, asyncio.Future[str]] = {}
        self._active_threads: Set[str] = set()

        # Setup message event handler
        self.app.event("message")(self._handle_message)

        logger.info("Slack client initialized")

    async def start(self) -> None:
        """Start the Slack client."""
        logger.info("Starting Slack client...")
        await self.handler.start_async()

    async def stop(self) -> None:
        """Stop the Slack client."""
        logger.info("Stopping Slack client...")
        await self.handler.close_async()

    async def ask_human(self, question: str, thread_ts: str | None = None) -> tuple[str, str]:
        """Ask a human a question via Slack and wait for response.
        If thread_ts is provided, continue in that thread; otherwise, create a new thread.
        Returns a tuple of (response, thread_ts).
        """
        logger.info(f"Asking human: {question[:100]}...")

        try:
            # Use existing thread or create a new one
            if not thread_ts:
                thread_ts = await self._create_thread(question)

            # Send the question with user mention
            message_text = f"<@{self.user_id}> {question}"
            await self.client.chat_postMessage(
                channel=self.channel_id,
                text=message_text,
                thread_ts=thread_ts,
            )

            # Wait for response
            response = await self._wait_for_response(thread_ts)
            logger.info("Received response from human")
            return response, thread_ts

        except Exception as e:
            logger.error(f"Error in ask_human: {e}")
            raise

    async def _create_thread(self, question: str) -> str:
        """Create a thread for the conversation."""
        # Use first 100 characters of question as thread title
        thread_title = question[:100].strip()
        if len(question) > 100:
            thread_title += "..."

        # Post initial message to create thread
        result = await self.client.chat_postMessage(
            channel=self.channel_id,
            text=f"🤖 *Question from AI Assistant*\n{thread_title}",
        )

        thread_ts = result.get("ts")
        if not isinstance(thread_ts, str):
            raise RuntimeError("Failed to get thread timestamp from Slack response.")
        self._active_threads.add(thread_ts)
        logger.debug(f"Created thread {thread_ts}")
        return thread_ts

    async def _wait_for_response(self, thread_ts: str, timeout: int = 600) -> str:
        """Wait for a human response in the specified thread."""
        future = asyncio.Future[str]()
        self._pending_responses[thread_ts] = future

        try:
            # Wait for response with timeout (10 minutes default)
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for response in thread {thread_ts}")
            raise Exception("Timeout waiting for human response")
        finally:
            # Clean up only pending responses, but keep active_threads for follow-ups
            self._pending_responses.pop(thread_ts, None)
            # self._active_threads.discard(thread_ts)  # Do NOT remove here

    async def _handle_message(self, event: dict, say) -> None:
        """Handle incoming Slack messages."""
        try:
            # Only process messages from the specified user
            if event.get("user") != self.user_id:
                return

            # Only process messages in active threads
            thread_ts = event.get("thread_ts")
            if not thread_ts or thread_ts not in self._active_threads:
                return

            # Get the message text
            message_text = event.get("text", "").strip()
            if not message_text:
                return

            # Check if we're waiting for a response in this thread
            if thread_ts in self._pending_responses:
                future = self._pending_responses[thread_ts]
                if not future.done():
                    future.set_result(message_text)
                    logger.debug(f"Received response in thread {thread_ts}")

        except Exception as e:
            logger.error(f"Error handling message: {e}")


class HumanInterface:
    """Interface for asking humans questions."""

    def __init__(self, slack_client: SlackClient):
        self.slack_client = slack_client

    async def ask(self, question: str, thread_ts: str | None = None) -> tuple[str, str]:
        """Ask a human a question and return their response and thread_ts."""
        return await self.slack_client.ask_human(question, thread_ts)
