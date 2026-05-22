import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import random

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'\n✅ Bot ist online als {bot.user}')
    print('Drücke Ctrl+C zum Beenden\n')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hallo {ctx.author.mention}! 👋')

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🧹 {amount} Nachrichten gelöscht!', delete_after=5)

@bot.command(name='say')
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)

@bot.command(name='userinfo')
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f'User Info - {member}', color=0x00ff00)
    embed.add_field(name='ID', value=member.id, inline=True)
    embed.add_field(name='Erstellt am', value=member.created_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name='Server beigetreten', value=member.joined_at.strftime('%d.%m.%Y') if member.joined_at else 'N/A', inline=True)
    await ctx.send(embed=embed)

@bot.command(name='serverinfo')
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f'Server Info - {guild.name}', color=0x00ff00)
    embed.add_field(name='Mitglieder', value=guild.member_count, inline=True)
    embed.add_field(name='Erstellt am', value=guild.created_at.strftime('%d.%m.%Y'), inline=True)
    await ctx.send(embed=embed)

@bot.command(name='meme')
async def meme(ctx):
    memes = [
        "https://i.imgur.com/1z2z3z4.jpg",
        "https://i.imgur.com/randommeme1.jpg",
        # Mehr hinzufügen
    ]
    await ctx.send(random.choice(memes) if memes else "No memes yet!")

@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(title="📜 Bot Commands", color=0x00ff00)
    embed.add_field(name="!ping", value="Bot Latenz", inline=False)
    embed.add_field(name="!hello", value="Begrüßung", inline=False)
    embed.add_field(name="!clear <anzahl>", value="Nachrichten löschen (Admin)", inline=False)
    embed.add_field(name="!say <text>", value="Bot sagt etwas (Admin)", inline=False)
    embed.add_field(name="!userinfo [@user]", value="User Info", inline=False)
    embed.add_field(name="!serverinfo", value="Server Info", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)
