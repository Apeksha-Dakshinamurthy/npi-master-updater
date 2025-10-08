# Deployment Plan for NPI_master_updater to LangGraph Platform

## Information Gathered
- Existing LangGraph graph is built in `NPI_master_updater/swarms/agents/graph.py` and compiled as `app`.
- State schema is `SwarmState` defined in `NPI_master_updater/swarms/structs/state.py`, which includes fields like `messages`, `input_data`, `planner_output`, etc.
- Dependencies are listed in root `requirements.txt`, but need updates for LangGraph Platform (e.g., langgraph>=0.2.0, langchain>=0.2).
- Tavily search tool is used via `langchain_community.tools.tavily_search`, requiring `tavily-python`.
- No existing `server.py` or `langgraph.json` for deployment.

## Plan
1. Create `NPI_master_updater/server.py` with a `create_app()` function that imports and returns the compiled graph from `graph.py`.
2. Create `NPI_master_updater/langgraph.json` config file pointing to the entrypoint.
3. Update root `requirements.txt` to include necessary dependencies for LangGraph Platform.

## Dependent Files to be edited
- `NPI_master_updater/server.py` (new file)
- `NPI_master_updater/langgraph.json` (new file)
- `requirements.txt` (update)

## Followup Steps
- Install `langgraph-cli` locally.
- Test locally with `langgraph dev --config NPI_master_updater/langgraph.json --port 8123`.
- Verify the API works (e.g., POST to /graphs/npi_updater/invoke with sample input).
- Commit and push changes to GitHub.
- Create deployment in LangSmith LangGraph Platform.
- Set environment variables (OPENAI_API_KEY, TAVILY_API_KEY, etc.).
- Consume the deployed API.
