import requests
import json
import os
from time import sleep

# ==== CONFIGURATION ====
ALMA_API_KEY = 'apikey'
BASE_URL = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/users'
HEADERS = {
    'Authorization': f'apikey {ALMA_API_KEY}',
    'Accept': 'application/json'
}
OUTPUT_DIR = 'alma_user_jsons'
REQUEST_DELAY = 0.25

# Sample list of institution IDs – or load from CSV as needed
# this is based on looking up by INST_ID value
inst_ids = [
    'userid'
    # Add more here or load from file
]

def fetch_full_user_record(inst_id):
    url = f"{BASE_URL}/{inst_id}"
    params = {'user_id_type': 'INST_ID'}
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch {inst_id} — {response.status_code}")
        return {'error': response.text, 'status_code': response.status_code}

def save_user_json(inst_id, data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = os.path.join(OUTPUT_DIR, f"{inst_id}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filename}")

def main():
    for idx, inst_id in enumerate(inst_ids):
        print(f"[{idx + 1}/{len(inst_ids)}] Fetching {inst_id}...")
        data = fetch_full_user_record(inst_id)
        save_user_json(inst_id, data)
        sleep(REQUEST_DELAY)

if __name__ == '__main__':
    main()
