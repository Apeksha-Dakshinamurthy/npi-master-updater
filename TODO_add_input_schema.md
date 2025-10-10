# TODO: Add Input Schema to StateGraph

## Steps:
1. [x] Update `NPI_master_updater/swarms/agents/graph.py`: Add import for SwarmInput and SwarmOutput, and modify StateGraph to include input=SwarmInput, output=SwarmOutput.
2. [x] Update `NPI_master_updater/server.py`: Remove import of schemas and .with_types call; directly use the compiled app from graph.py. (app.py deleted as not needed)
3. [x] Fix TypedDict issue in `NPI_master_updater/swarms/structs/state.py`: Use typing_extensions.TypedDict instead of typing.TypedDict.
4. [x] Verify the changes by running the application or testing the graph.
