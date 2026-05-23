import discord
from discord.ext import commands
import requests
import re
from bs4 import BeautifulSoup

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="insta")
    async def instagram_profile(self, ctx, url_or_username: str):
        """Holt das Profilbild von Instagram und zeigt es groß im Chat"""
        await ctx.channel.typing()

        # Username sauber extrahieren
        match = re.search(r"(?:instagram\.com/|www\.instagram\.com/|@)?([a-zA-Z0-9._]+)", url_or_username)
        if not match:
            return await ctx.send("❌ Ungültiger Instagram-Link oder Username!")
        
        username = match.group(1).strip().lower()

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            # Versuch über Imginn Proxy für bessere Ergebnisse
            proxy_url = f"https://imginn.com/{username}/"
            response = requests.get(proxy_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Suche nach Profilbild
                img_tag = soup.find('img', class_=lambda x: x and ('profile' in x.lower() or 'pic' in x.lower()))
                if img_tag and img_tag.get('src'):
                    pfp_url = img_tag['src']
                else:
                    pfp_url = f"https://www.instagram.com/{username}/"
            else:
                pfp_url = f"https://www.instagram.com/{username}/"

            embed = discord.Embed(
                title=f"📸 Instagram Profil: @{username}",
                color=0xE1306C
            )
            embed.set_image(url=pfp_url)
            embed.set_footer(text="Profilbild wird direkt angezeigt • Private Profile nur teilweise möglich")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Konnte das Profil nicht laden.\nVersuch es mit einem öffentlichen Profil oder später nochmal.")

async def setup(bot):
    await bot.add_cog(Utility(bot))