import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your actual deployment URL
DEPLOYMENT_URL = "https://npi-master-updater-deployme-753d7f75157e5eb5be7da775fce026e7.us.langgraph.app/invoke"

# Sample input from dataset
input_data = {
    "PROVIDER_FIRST_NAME": "SUSAN",
    "PROVIDER_MIDDLE_NAME": "L",
    "PROVIDER_LAST_NAME_LEGAL_NAME": "ROEDER",
    "CLASSIFICATION": "INTERNAL MEDICINE",
    "NPI": 1487615340,
    "PRIMARY_AFFILIATION_NAME": "IOWA CITY VA HEALTH CARE SYSTEM"
}

headers = {
    "Content-Type": "application/json",
    "x-api-key": os.getenv("LANGSMITH_API_KEY")
}

response = requests.post(DEPLOYMENT_URL, headers=headers, data=json.dumps(input_data))

if response.status_code == 200:
    result = response.json()
    print("Success:", result)
else:
    print("Error:", response.status_code, response.text)
