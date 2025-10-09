import requests
import json
import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

DEPLOYMENT_URL = "https://npi-master-updater-deployme-753d7f75157e5eb5be7da775fce026e7.us.langgraph.app/runs/wait"


client = Client()
examples = list(client.list_examples(dataset_name="npi_1_testset"))
print(examples)
if not examples:
    print("No examples in dataset")
    exit(1)


example = examples[0]
row = example.inputs

print(f"Using example: {row}")

payload = {
    "assistant_id": "ce66557e-6564-4287-85ed-06a037b34de4",
    "input": row
}

headers = {
    "Content-Type": "application/json",
    "x-api-key": os.getenv("LANGSMITH_API_KEY")
}

response = requests.post(DEPLOYMENT_URL, headers=headers, data=json.dumps(payload), timeout=(10, 600))

if response.status_code == 200:
    result = response.json()
    print("Success:", result)
else:
    print("Error:", response.status_code, response.text)
