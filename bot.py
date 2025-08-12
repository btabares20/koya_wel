import os
import requests
import discord
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
API_KEY = os.getenv("API_NINJAS_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

FACTS_URL = "https://api.api-ninjas.com/v1/facts"
HOROSCOPE_URL = "https://api.api-ninjas.com/v1/horoscope"

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# /facts command
@tree.command(name="facts", description="Get a random fact")
async def facts_command(interaction: discord.Interaction):
    resp = requests.get(FACTS_URL, headers={"X-Api-Key": API_KEY})
    if resp.status_code != 200:
        await interaction.response.send_message("Error fetching facts.", ephemeral=True)
        return
    fact = resp.json()[0]["fact"]

    embed = discord.Embed(
        title="<:aaaa:1404611331868332123> Bigyan ng Pak!!",
        description=fact,
        color=0x00FFAA,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="Powered by Koya Wel")
    await interaction.response.send_message(embed=embed)

# /horos command
@tree.command(name="horos", description="Get today's horoscope for your sign")
@app_commands.describe(sign="Your zodiac sign (e.g., aries, taurus, sagittarius)")
async def horos_command(interaction: discord.Interaction, sign: str):
    resp = requests.get(f"{HOROSCOPE_URL}?zodiac={sign.lower()}", headers={"X-Api-Key": API_KEY})
    if resp.status_code != 200:
        await interaction.response.send_message("Error fetching horoscope.", ephemeral=True)
        return
    data = resp.json()
    horoscope_text = data.get("horoscope", "No horoscope available.")

    embed = discord.Embed(
        title=f"<:dasalasananses:1404298595204857897> Gusto mo zodiac sa {sign.capitalize()}?",
        description=horoscope_text,
        color=0xFFD700,
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text="Powered by Dasalasananses")
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_ready():
    await tree.sync()  # Sync slash commands
    print(f"Bot logged in as {bot.user}")

bot.run(DISCORD_BOT_TOKEN)
