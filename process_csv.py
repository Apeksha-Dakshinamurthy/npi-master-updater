import asyncio
from langsmith import Client
from main import run_swarm

async def show_dataset():
    client = Client()
    examples = list(client.list_examples(dataset_name="npi_1_testset"))

    print(f"Total examples in dataset: {len(examples)}")

    for i, example in enumerate(examples):
        print(f"\nExample {i+1}:")
        print(f"Inputs: {example.inputs}")

        # Map inputs to input_data format
        input_data = {
            "first_name": example.inputs.get('PROVIDER_FIRST_NAME', ''),
            "middle_name": example.inputs.get('PROVIDER_MIDDLE_NAME', ''),
            "last_name": example.inputs.get('PROVIDER_LAST_NAME_LEGAL_NAME', ''),
            "classification": example.inputs.get('CLASSIFICATION', ''),
            "npi_number": str(example.inputs.get('NPI', '')),
            "primary_affiliation_name": example.inputs.get('PRIMARY_AFFILIATION_NAME', '')
        }

        print(f"Mapped input_data: {input_data}")

        # Process through swarm
        try:
            result = await run_swarm(input_data)
            print(f"Swarm Output: {result}")
        except Exception as e:
            print(f"Error processing: {str(e)}")

        if example.outputs:
            print(f"Dataset Outputs: {example.outputs}")
        print("---")

if __name__ == "__main__":
    asyncio.run(show_dataset())
