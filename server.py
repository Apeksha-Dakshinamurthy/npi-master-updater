from langchain_core.runnables import RunnableLambda
from swarms.agents.graph import app as base_app  # compiled graph

def _adapt_payload(payload: dict) -> dict:
    # Platform/Experiments send: {"assistant_id": "...", "input": {...row...}}
    row = payload.get("input") if isinstance(payload.get("input"), dict) else payload

    input_data = {
        "first_name": row.get("PROVIDER_FIRST_NAME", ""),
        "middle_name": row.get("PROVIDER_MIDDLE_NAME", ""),
        "last_name": row.get("PROVIDER_LAST_NAME_LEGAL_NAME", ""),
        "classification": row.get("CLASSIFICATION", ""),
        "npi_number": str(row.get("NPI", "")),
        "primary_affiliation_name": row.get("PRIMARY_AFFILIATION_NAME", ""),
    }
    # Build the same initial state you use in run_swarm()
    state = {
        "input_data": input_data,
        "short_term_memory": [],
        # helpful debug so you can see this ran in LangSmith traces
        "debug_adapt_server": True,
        "raw_row": row,
    }
    return state

# Wrap: adapter → your compiled graph

def create_app():
    app = RunnableLambda(_adapt_payload) | base_app
    return app
