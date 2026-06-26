import os
from collections import defaultdict, deque

import discord
from discord.ext import commands
from anthropic import AsyncAnthropic

# Claude-Modell (Anthropics leistungsstärkstes Opus-Modell)
MODEL = "claude-opus-4-8"
# Maximale Antwortlänge in Tokens (bewusst klein gehalten für Chat-Antworten)
MAX_TOKENS = 1024
# Wie viele Nachrichten (User + Assistant) pro Kanal gemerkt werden
HISTORY_LIMIT = 20
# Discord erlaubt maximal 2000 Zeichen pro Nachricht
DISCORD_LIMIT = 2000

SYSTEM_PROMPT = (
    "Du bist ein hilfsbereiter Assistent in einem Discord-Server, angetrieben von Claude. "
    "Antworte freundlich und natürlich in der Sprache des Nutzers (meistens Deutsch). "
    "Halte dich kurz und passend für einen Chat – lange Aufsätze vermeiden. "
    "Du kannst Discord-Markdown verwenden."
)


def split_message(text: str, limit: int = DISCORD_LIMIT):
    """Teilt lange Antworten in Discord-taugliche Stücke (<= limit Zeichen)."""
    chunks = []
    while len(text) > limit:
        # An einem Zeilenumbruch innerhalb des Limits trennen, sonst hart schneiden
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    if text:
        chunks.append(text)
    return chunks


class ClaudeChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncAnthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung
        # Gesprächsverlauf pro Kanal
        self.history = defaultdict(lambda: deque(maxlen=HISTORY_LIMIT))

    async def _respond(self, channel, channel_id: int, prompt: str):
        """Schickt den Verlauf an Claude und antwortet im Kanal."""
        history = self.history[channel_id]
        history.append({"role": "user", "content": prompt})

        try:
            async with channel.typing():
                response = await self.client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM_PROMPT,
                    messages=list(history),
                )
        except Exception as e:
            # Den fehlgeschlagenen User-Turn wieder entfernen, damit der Verlauf gültig bleibt
            if history and history[-1]["role"] == "user":
                history.pop()
            await channel.send(f"❌ Claude-Fehler: {e}")
            return

        reply = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

        if not reply:
            reply = "🤔 (keine Antwort erhalten)"

        history.append({"role": "assistant", "content": reply})

        for chunk in split_message(reply):
            await channel.send(chunk)

    @commands.command(name="ai")
    async def ai(self, ctx, *, message: str):
        """Stellt Claude eine Frage: !ai <Nachricht>"""
        await self._respond(ctx.channel, ctx.channel.id, message)

    @commands.command(name="reset")
    async def reset(self, ctx):
        """Löscht den Gesprächsverlauf für diesen Kanal."""
        self.history.pop(ctx.channel.id, None)
        await ctx.send("🧹 Gesprächsverlauf zurückgesetzt!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Eigene Nachrichten und andere Bots ignorieren
        if message.author.bot:
            return
        # Präfix-Befehle (z. B. !ai) werden separat behandelt
        if message.content.startswith(self.bot.command_prefix):
            return
        # Nur reagieren, wenn der Bot direkt erwähnt wird
        if self.bot.user not in message.mentions:
            return

        # Die Erwähnung aus dem Text entfernen
        prompt = message.content
        for mention in (f"<@{self.bot.user.id}>", f"<@!{self.bot.user.id}>"):
            prompt = prompt.replace(mention, "")
        prompt = prompt.strip()

        if not prompt:
            await message.channel.send(
                f"Hallo {message.author.mention}! 👋 Frag mich etwas, oder nutze `!ai <Nachricht>`."
            )
            return

        await self._respond(message.channel, message.channel.id, prompt)


async def setup(bot):
    await bot.add_cog(ClaudeChat(bot))
