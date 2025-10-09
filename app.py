from swarms.schemas import SwarmInput, SwarmOutput
from swarms.agents.graph import workflow

# Compile the graph with Pydantic input/output schemas
runnable = workflow.compile().with_types(input_type=SwarmInput, output_type=SwarmOutput)
