# CLAUDE.md

Guidance for AI assistants (and humans) working in this repository.

## What this is

A small **Discord bot** written in Python with [discord.py](https://discordpy.readthedocs.io/).
It exposes a handful of chat/moderation commands (prefix `!`) plus an Instagram
profile-picture lookup, and — as of the Claude integration — can hold a
conversation with users directly in Discord using the Anthropic Claude API.

The codebase and most user-facing strings are in **German**. Match that
convention when adding new commands or messages.

## Layout

```
discord-bot/
├── bot.py              # Entry point: bot instance, inline commands, extension loading
├── cogs/
│   ├── utility.py      # Utility cog: !insta (Instagram profile picture via imginn proxy)
│   └── claude_chat.py  # Claude cog: chat with Claude in Discord (mention or !ai)
├── requirements.txt    # Python dependencies
├── README.md           # User-facing setup instructions (German)
└── CLAUDE.md           # This file
```

## How it runs

1. Install deps: `pip install -r requirements.txt`
2. Create a `.env` file in the repo root:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   ANTHROPIC_API_KEY=your_anthropic_api_key   # required for the Claude chat cog
   ```
3. Start: `python bot.py`

There is no build step, no test suite, and no linter configured. "Running it"
means launching the bot against a real Discord application token. The console is
the only dashboard — status and errors print to stdout.

## Architecture notes

- **Entry point** is `bot.py`. It builds a single `commands.Bot` with prefix `!`
  and the `message_content` + `members` privileged intents (both must be enabled
  in the Discord Developer Portal, or commands/chat won't receive content).
- **Commands** live in two places:
  - Simple ones are defined inline in `bot.py` with `@bot.command(...)`
    (`!ping`, `!hello`, `!clear`, `!say`, `!userinfo`, `!serverinfo`, `!meme`,
    `!help`).
  - Grouped/feature commands live in **cogs** under `cogs/`, loaded as
    extensions in `bot.setup_hook`. Each cog file ends with an
    `async def setup(bot)` that calls `await bot.add_cog(...)`.
- **Adding a cog:** create `cogs/<name>.py` with a `commands.Cog` subclass and a
  `setup` coroutine, then add `'cogs.<name>'` to the extension list in
  `bot.setup_hook` in `bot.py`.
- **Async everywhere.** discord.py is asyncio-based. Use `await` for Discord and
  network calls. For the Claude integration, use the **async** Anthropic client
  (`AsyncAnthropic`) so the event loop is never blocked. The legacy `requests`
  call in `cogs/utility.py` is synchronous and will block the loop — prefer
  `aiohttp`/async HTTP for new network code.

## Claude integration (`cogs/claude_chat.py`)

- Uses the official Anthropic Python SDK (`anthropic`) via `AsyncAnthropic()`,
  which reads `ANTHROPIC_API_KEY` from the environment.
- Default model: **`claude-opus-4-8`** (Anthropic's most capable Opus-tier
  model). Only change the model string if explicitly asked.
- The bot replies when it is **@mentioned** or when a user runs **`!ai <text>`**.
  `!reset` clears the per-channel conversation history.
- Conversation history is kept **per channel** in memory (capped), so the bot
  loses context on restart. The Messages API is stateless — the full history is
  re-sent on every call.
- Responses are split into ≤2000-character chunks to respect Discord's message
  limit; `max_tokens` is kept modest to keep replies chat-sized.

### Anthropic API conventions (important for AI assistants)

- This repo targets **Claude Opus 4.8** (`claude-opus-4-8`). Model IDs are exact
  strings — never append date suffixes.
- On Opus 4.8: `thinking` is adaptive-only (`{"type": "adaptive"}`); the legacy
  `budget_tokens` and the sampling params `temperature`/`top_p`/`top_k` are
  **removed** and return HTTP 400. Assistant-turn prefills also 400.
- `response.content` is a list of typed blocks — check `block.type == "text"`
  before reading `block.text`.
- Prefer streaming (`messages.stream()`) for long outputs; for short Discord
  replies a single `messages.create()` is fine.
- When unsure about the API surface, consult the `claude-api` skill rather than
  guessing.

## Conventions & gotchas

- **Language:** German for user-facing strings and most comments.
- **Secrets:** load from `.env` via `python-dotenv`; never commit tokens. `.env`
  is not tracked.
- **Privileged intents:** `message_content` and `members` are required and must
  be toggled on in the Developer Portal.
- **`utility.py` depends on `requests` and `beautifulsoup4`** — both must be in
  `requirements.txt` for the cog to import.
- **No tests/CI.** Verify changes by running the bot against a test server.
