import asyncio
from langsmith import evaluate
from main import run_swarm
from dotenv import load_dotenv

load_dotenv()

async def eval_function(inputs):
    # Map inputs to input_data format
    input_data = {
        "first_name": inputs.get('PROVIDER_FIRST_NAME', ''),
        "middle_name": inputs.get('PROVIDER_MIDDLE_NAME', ''),
        "last_name": inputs.get('PROVIDER_LAST_NAME_LEGAL_NAME', ''),
        "classification": inputs.get('CLASSIFICATION', ''),
        "npi_number": str(inputs.get('NPI', '')),
        "primary_affiliation_name": inputs.get('PRIMARY_AFFILIATION_NAME', '')
    }

    # Process through swarm
    result = await run_swarm(input_data)
    return result

def sync_eval_function(inputs):
    # Since evaluate expects a sync function, but run_swarm is async, use asyncio.run
    return asyncio.run(eval_function(inputs))

if __name__ == "__main__":
    # Run experiment on LangSmith
    results = evaluate(
        sync_eval_function,
        data="npi_1_testset",
        description="NPI Updater Experiment",
        num_repetitions=1
    )
    print("Experiment completed. Results:", results)
