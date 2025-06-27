# Human-in-the-Loop MCP Server for Slack

A Python-based MCP (Model Context Protocol) server that allows AI assistants to ask questions to humans via Slack.

## Features

- 🤖 **MCP Integration**: Full MCP server implementation with tools capability
- 💬 **Slack Integration**: Uses Slack threads for organized conversations
- 🔄 **Async Support**: Built with modern async/await patterns
- 🛡️ **Error Handling**: Robust error handling and graceful shutdown
- 📝 **Logging**: Comprehensive logging with loguru
- ⚡ **Minimal & Clean**: Focused, maintainable codebase

## Overview

This MCP server enables AI assistants to request information from humans when they need:
- Personal preferences or opinions
- Project-specific context or decisions
- Local environment details
- Non-public or undocumented information
- Human judgment on ambiguous situations

## Requirements

- Python 3.11+
- Slack workspace with bot permissions
- MCP-compatible AI client (Claude Desktop, etc.)

## Installation

### Using uv (Recommended)

```bash
git clone <repository-url>
cd human-in-the-loop-slack
uv sync
```

### Using pip

```bash
git clone <repository-url>
cd human-in-the-loop-slack
pip install -e .
```

## Slack Setup

### 1. Create a Slack App

1. Go to [Slack API](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app and select your workspace

### 2. Configure Bot Permissions

In your app settings, go to **OAuth & Permissions** and add these scopes:

**Bot Token Scopes:**
- `channels:read` - View basic information about public channels
- `chat:write` - Send messages as the bot
- `chat:write.public` - Send messages to channels the bot isn't a member of
- `users:read` - View people in the workspace

### 3. Enable Socket Mode

1. Go to **Socket Mode** in your app settings
2. Enable Socket Mode
3. Generate an **App-Level Token** with `connections:write` scope
4. Save the token (this is your `SLACK_APP_TOKEN`)

### 4. Install App to Workspace

1. Go to **OAuth & Permissions**
2. Click "Install to Workspace"
3. Copy the **Bot User OAuth Token** (this is your `SLACK_BOT_TOKEN`)

### 5. Get Channel and User IDs

**Channel ID:**
1. Right-click on the channel in Slack
2. Select "Copy link"
3. The ID is the last part: `https://workspace.slack.com/archives/C1234567890`

**User ID:**
1. Right-click on your profile in Slack
2. Select "Copy member ID"

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
export SLACK_APP_TOKEN="xapp-..."
export SLACK_BOT_TOKEN="xoxb-..."
```

### Command Line Usage

```bash
# Basic usage
uv run human-in-the-loop --slack-channel-id C1234567890 --slack-user-id U0987654321

# With custom log level
uv run human-in-the-loop \
  --slack-channel-id C1234567890 \
  --slack-user-id U0987654321 \
  --log-level DEBUG

# Override tokens via command line (not recommended)
uv run human-in-the-loop \
  --slack-channel-id C1234567890 \
  --slack-user-id U0987654321 \
  --slack-app-token "xapp-..." \
  --slack-bot-token "xoxb-..."
```

## MCP Client Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "human-in-the-loop": {
      "command": "uv",
      "args": [
        "run", "human-in-the-loop",
        "--slack-channel-id", "C1234567890",
        "--slack-user-id", "U0987654321"
      ],
      "env": {
        "SLACK_APP_TOKEN": "xapp-...",
        "SLACK_BOT_TOKEN": "xoxb-..."
      }
    }
  }
}
```

### Claude Code

For Claude Code, add to your MCP settings:

```json
{
  "mcpServers": {
    "human-in-the-loop": {
      "command": "uv",
      "args": [
        "run", "human-in-the-loop",
        "--slack-channel-id", "C1234567890",
        "--slack-user-id", "U0987654321"
      ]
    }
  }
}
```

Set environment variables before running:

```bash
export SLACK_APP_TOKEN="xapp-..."
export SLACK_BOT_TOKEN="xoxb-..."
claude
```

## Usage Example

```
Human: Please create a project roadmap. Ask me for input on priorities.
Assistant: I'll create a project roadmap and ask for your input on priorities.
[Uses ask_human tool to post question in Slack]
```

The AI posts a question in your designated Slack channel, mentions you, and waits for your response. When you reply in the thread, the response is returned to the AI.

## How It Works

1. AI assistant calls the `ask_human` tool with a question
2. MCP server posts the question in a Slack thread and mentions the specified user
3. Human responds in the Slack thread
4. Response is captured and returned to the AI assistant
5. AI continues with the human's input

## Project Structure

```
src/
└── human_in_the_loop/
    ├── __init__.py
    ├── main.py              # CLI entry point and server orchestration
    ├── config.py            # Configuration management
    ├── slack/
    │   ├── __init__.py
    │   └── client.py        # Slack integration and communication
    └── mcp/
        ├── __init__.py
        ├── server.py        # MCP server implementation
        └── tools.py         # MCP tools definition
```

## Development

### Setup Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd human-in-the-loop-slack
uv sync --dev
```

### Adding New Tools

To add new MCP tools, modify `src/human_in_the_loop/mcp/tools.py`:

```python
def get_tools(self) -> List[Tool]:
    return [
        # existing tools...
        Tool(
            name="your_new_tool",
            description="Description of your tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param"],
            },
        ),
    ]
```

### Logging

Increase log level for debugging:

```bash
uv run human-in-the-loop \
  --slack-channel-id C1234567890 \
  --slack-user-id U0987654321 \
  --log-level DEBUG
```

## Security Considerations

- Store tokens securely (use environment variables, not command line)
- Limit bot permissions to minimum required
- Consider using private channels for sensitive conversations
- Review message history access policies

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run linting and tests
6. Submit a pull request