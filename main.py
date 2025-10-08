import os
from dotenv import load_dotenv
from swarms.agents.graph import app
import asyncio

load_dotenv()

print("LANGSMITH_PROJECT:", os.environ.get("LANGSMITH_PROJECT"))
print("LANGSMITH_API_KEY:", os.environ.get("LANGSMITH_API_KEY")[:10] + "..." if os.environ.get("LANGSMITH_API_KEY") else "Not set")

async def run_swarm(input_data: dict) -> dict:
    initial_state = {
        "input_data": input_data,
        "short_term_memory": []  
    }
    result = await app.ainvoke(initial_state)

    # Return only the final_output field, not the entire state
    return result.get("final_output", {"error": "No final output generated"})

if __name__ == "__main__":
    import asyncio

    async def main():
        #sample input
        input_data = {
            "first_name": "SAIAMA",
            "middle_name": "NAHEED",
            "last_name": "WAQAR",
            "classification": "INTERNAL MEDICINE",
            "npi_number": "1083703383",
            "primary_affiliation_name": "WASHINGTON UNIVERSITY"
        }
        result = await run_swarm(input_data)
        print("Final Output:", result)

    asyncio.run(main())

