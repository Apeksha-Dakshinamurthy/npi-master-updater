from typing import TypedDict, Optional, List, Annotated, Any
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class SwarmState(TypedDict,total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    active_agent: str
    input: Optional[dict[str, Any]]          # NEW: raw input bucket
    raw_row: Optional[dict[str, Any]]        # OPTIONAL: keep original row
    input_data: Annotated[dict, lambda x, y: y]  # Use lambda to handle concurrent updates
    planner_output: Annotated[Optional[dict], lambda x, y: y]  # Handle concurrent updates from agents
    nppes_output: Optional[dict]
    private_output: Optional[dict]
    planner_sup_output: Optional[dict]
    candidate_output: Optional[dict]
    candidate_sup_output: Optional[dict]
    selector_output: Optional[dict]
    selector_sup_output: Optional[dict]
    enricher_output: Optional[dict]
    enricher_sup_output: Optional[dict]
    validator_output: Optional[dict]
    final_output: Optional[dict]
    short_term_memory: Annotated[List[dict], lambda x, y: (x or []) + (y or [])]  # Accumulate memory entries
