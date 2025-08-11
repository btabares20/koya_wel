import os
import time
import requests
from datetime import datetime, timezone

api_key = os.getenv("API_NINJAS_KEY")
discord_webhook = os.getenv("DISCORD_WEBHOOK")

if not api_key:
    raise ValueError("API_NINJAS_KEY environment variable not set.")
if not discord_webhook:
    raise ValueError("DISCORD_WEBHOOK environment variable not set.")

api_url = f"https://api.api-ninjas.com/v1/facts"
INTERVAL = 900

while True:
    response = requests.get(api_url, headers={'X-Api-Key': api_key})

    if response.status_code != requests.codes.ok:
        raise RuntimeError(f"Error fetching facts: {response.status_code} {response.text}")

    facts = response.json()

    field = [{
        "name": "Pak",
        "value": facts[0]["fact"],
        "inline":False
    }]
    payload = {
        "embeds": [
            {
                "title": "<:dasalasananses:1404298595204857897> Bigyan ng Daily Paks!",
                "description": f"AAAAAA PAWBTAWSAN!",
                "color": 0x00FFAA,
                "fields": field,
                "footer": {"text": "Powered by Koya Wel"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
    }

    discord_response = requests.post(discord_webhook, json=payload)

    if discord_response.status_code != 204:
        raise RuntimeError(f"Error sending to Discord: {discord_response.status_code} {discord_response.text}")

    print("Facts sent to Discord with custom embed successfully.")

    time.sleep(INTERVAL)

