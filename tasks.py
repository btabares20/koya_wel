import os
import asyncio
from datetime import datetime, timezone
import aiohttp

api_key = os.getenv("API_NINJAS_KEY")
discord_webhook = os.getenv("DISCORD_WEBHOOK")
discord_webhook_horoscope = os.getenv("DISCORD_WEBHOOK_HORO")

if not api_key:
    raise ValueError("API_NINJAS_KEY environment variable not set.")
if not discord_webhook:
    raise ValueError("DISCORD_WEBHOOK environment variable not set.")
if not discord_webhook_horoscope:
    raise ValueError("DISCORD_WEBHOOK_HORO environment variable not set.")

FACTS_INTERVAL = 900  # 15 minutes
HOROSCOPE_INTERVAL = 86400  # 24 hours

signs = {
    "sagittarius": "♐",
    "pisces": "♓"
}

async def send_horoscopes(session):
    horoscope_url = "https://api.api-ninjas.com/v1/horoscope"
    horoscope_fields = []

    for sign, emoji in signs.items():
        async with session.get(f"{horoscope_url}?zodiac={sign}", headers={'X-Api-Key': api_key}) as resp:
            if resp.status != 200:
                horoscope_text = f"Error fetching horoscope: {resp.status}"
            else:
                horoscope_json = await resp.json()
                horoscope_text = horoscope_json.get("horoscope", "No horoscope available.")
            horoscope_fields.append({
                "name": f"{emoji} {sign.capitalize()}",
                "value": horoscope_text,
                "inline": False
            })

    horoscope_payload = {
        "embeds": [
            {
                "title": "🔮 Daily Horoscopes",
                "description": "Your fortune for today:",
                "color": 0xFFD700,
                "fields": horoscope_fields,
                "footer": {"text": "Powered by API Ninjas"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
    }

    async with session.post(discord_webhook_horoscope, json=horoscope_payload) as discord_resp:
        if discord_resp.status != 204:
            text = await discord_resp.text()
            raise RuntimeError(f"Error sending horoscope to Discord: {discord_resp.status} {text}")

    print("Horoscopes sent to Discord successfully.")

async def send_facts(session):
    facts_url = "https://api.api-ninjas.com/v1/facts"
    fact_response = await session.get(facts_url, headers={'X-Api-Key': api_key})
    if fact_response.status != 200:
        text = await fact_response.text()
        raise RuntimeError(f"Error fetching facts: {fact_response.status} {text}")

    fact_data = await fact_response.json()

    fact_payload = {
        "embeds": [
            {
                "title": "<:dasalasananses:1404298595204857897> Bigyan ng Daily Paks!",
                "description": "AAAAAA PAWBTAWSAN!",
                "color": 0x00FFAA,
                "fields": [
                    {
                        "name": "Pak",
                        "value": fact_data[0]["fact"],
                        "inline": False
                    }
                ],
                "footer": {"text": "Powered by Koya Wel"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
    }

    discord_response = await session.post(discord_webhook, json=fact_payload)
    if discord_response.status != 204:
        text = await discord_response.text()
        raise RuntimeError(f"Error sending fact to Discord: {discord_response.status} {text}")

    print("Fact sent to Discord successfully.")

async def horoscope_task():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await send_horoscopes(session)
            except Exception as e:
                print(f"Horoscope task error: {e}")
            await asyncio.sleep(HOROSCOPE_INTERVAL)

async def facts_task():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await send_facts(session)
            except Exception as e:
                print(f"Facts task error: {e}")
            await asyncio.sleep(FACTS_INTERVAL)

async def main():
    # Run both tasks concurrently
    await asyncio.gather(
        horoscope_task(),
        facts_task()
    )

if __name__ == "__main__":
    asyncio.run(main())

