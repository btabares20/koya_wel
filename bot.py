import os
import asyncio
import requests
import discord
from contextlib import asynccontextmanager
from discord import app_commands
from fastapi import FastAPI
from datetime import datetime, timezone
import uvicorn
import httpx

API_KEY = os.getenv("API_NINJAS_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

FACTS_URL = "https://api.api-ninjas.com/v1/facts"
HOROSCOPE_URL = "https://api.api-ninjas.com/v1/horoscope"

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(ping_self())
    yield  
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

async def ping_self():
    while True:
        try:
            url = os.getenv("APP_URL", f"http://localhost:{os.environ.get('PORT', 8000)}")
            async with httpx.AsyncClient() as client:
                await client.get(url)
            print(f"Pinged self at {url}")
        except Exception as e:
            print(f"Self-ping failed: {e}")
        await asyncio.sleep(10 * 60) # 10 minutes

app.router.lifespan_context = lifespan

@app.get("/")
async def root():
    return {"status": "Bot is running"}


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

@tree.command(name="horoscope", description="Get today's horoscope for your sign")
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
    await tree.sync()
    print(f"Bot logged in as {bot.user}")

async def start_discord_bot():
    await bot.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    import threading

    def run_fastapi():
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)

    threading.Thread(target=run_fastapi, daemon=True).start()
    asyncio.run(start_discord_bot())

