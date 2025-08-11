import os
import time
import requests
from datetime import datetime, timezone

api_key = os.getenv("API_NINJAS_KEY")
discord_webhook = os.getenv("DISCORD_WEBHOOK")
discord_webhook_horoscope = os.getenv("DISCORD_WEBHOOK_HORO")

if not api_key:
    raise ValueError("API_NINJAS_KEY environment variable not set.")
if not discord_webhook:
    raise ValueError("DISCORD_WEBHOOK environment variable not set.")
if not discord_webhook_horoscope:
    raise ValueError("DISCORD_WEBHOOK_HORO environment variable not set.")

facts_url = "https://api.api-ninjas.com/v1/facts"
horoscope_url = "https://api.api-ninjas.com/v1/horoscope"

signs = {
    "sagittarius": "♐",
    "pisces": "♓"
}

FACTS_INTERVAL = 900  # 15 minutes

horoscope_fields = []
for sign, emoji in signs.items():
    resp = requests.get(f"{horoscope_url}?zodiac={sign}", headers={'X-Api-Key': api_key})
    if resp.status_code != requests.codes.ok:
        horoscope_text = f"Error fetching horoscope: {resp.status_code}"
    else:
        horoscope_json = resp.json()
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

discord_response = requests.post(discord_webhook_horoscope, json=horoscope_payload)
if discord_response.status_code != 204:
    raise RuntimeError(f"Error sending horoscope to Discord: {discord_response.status_code} {discord_response.text}")

print("Horoscopes sent to Discord successfully.")

while True:
    fact_response = requests.get(facts_url, headers={'X-Api-Key': api_key})
    if fact_response.status_code != requests.codes.ok:
        raise RuntimeError(f"Error fetching facts: {fact_response.status_code} {fact_response.text}")

    fact_data = fact_response.json()

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

    discord_response = requests.post(discord_webhook, json=fact_payload)
    if discord_response.status_code != 204:
        raise RuntimeError(f"Error sending fact to Discord: {discord_response.status_code} {discord_response.text}")

    print("Fact sent to Discord successfully.")
    time.sleep(FACTS_INTERVAL)

