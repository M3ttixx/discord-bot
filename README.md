# Discord Bot

Ein einfacher Discord Bot mit vielen Funktionen und CMD Dashboard.

## Installation

1. Repository klonen: `git clone https://github.com/M3ttixx/discord-bot.git`
2. `cd discord-bot`
3. `pip install -r requirements.txt`
4. Erstelle eine `.env`-Datei:
   ```
   DISCORD_TOKEN=dein_bot_token_hier
   ANTHROPIC_API_KEY=dein_anthropic_api_key_hier
   ```
   Den Anthropic API Key bekommst du unter https://console.anthropic.com/
   (nur nötig für die Claude-Chatfunktion).
5. Bot Token im Discord Developer Portal holen und Bot zum Server einladen.
   Aktiviere dort die Privileged Intents **Message Content** und **Server Members**.
6. Starte den Bot: `python bot.py`

## Features
- `!ping` — Latenz checken
- `!hello` — Begrüßung
- `!clear <anzahl>` — Nachrichten löschen (Admin)
- `!say <text>` — Bot sagt etwas (Admin)
- `!userinfo [@user]` — User Informationen
- `!serverinfo` — Server Informationen
- `!insta <username>` — Instagram Profilbild anzeigen
- `!help` — Diese Hilfe
- CMD Dashboard: Alle Logs und Status werden direkt in der Konsole angezeigt.

## 🤖 Claude Chat
Der Bot kann dank der Anthropic Claude API direkt mit dir chatten:
- **@Bot erwähnen** — schreib den Bot in einer Nachricht an und stelle deine Frage
- `!ai <Nachricht>` — Claude eine Frage stellen
- `!reset` — Gesprächsverlauf des Kanals zurücksetzen

Der Verlauf wird pro Kanal gemerkt, damit Claude den Kontext behält.

Du kannst leicht weitere Commands hinzufügen!

Viel Spaß! 🚀