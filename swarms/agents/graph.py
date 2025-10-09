from langgraph.graph import StateGraph, START, END
from .planner import PlannerAgent
from .nppes_agent import NPPESAgent
from .privateclinic_agent import PrivateClinicAgent
from .planner_supervisor import PlannerSupervisor
from .candidate_extractor_agent import CandidateExtractorAgent
from .candidate_extractor_supervisor import CandidateExtractorSupervisor
from .selector_agent import SelectorAgent
from .selector_supervisor import SelectorSupervisor
from .enricher_agent import EnricherAgent
from .enricher_supervisor import EnricherSupervisor
from .validator_agent import ValidatorAgent
from .validator_supervisor import ValidatorSupervisor
from ..structs.state import SwarmState

# Define node functions
def planner_node(state: SwarmState) -> SwarmState:
    # If input_data not present (e.g., from LangSmith experiment), map the state inputs
    if "input_data" not in state:
        state["input_data"] = {
            "first_name": state.get('PROVIDER_FIRST_NAME', ''),
            "middle_name": state.get('PROVIDER_MIDDLE_NAME', ''),
            "last_name": state.get('PROVIDER_LAST_NAME_LEGAL_NAME', ''),
            "classification": state.get('CLASSIFICATION', ''),
            "npi_number": str(state.get('NPI', '')),
            "primary_affiliation_name": state.get('PRIMARY_AFFILIATION_NAME', '')
        }
        # Initialize short_term_memory if not present
        if "short_term_memory" not in state:
            state["short_term_memory"] = []

    #new_state = state.copy()
    planner = PlannerAgent()
    state["planner_output"] = planner.process(state)
    if 'raw_response' in state["planner_output"]:
        raw_response = state["planner_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Planner Output:", state["planner_output"])
    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "planner",
        "output": state["planner_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state

def nppes_node(state: SwarmState) -> SwarmState:
    nppes = NPPESAgent()
    state["nppes_output"] = nppes.process(state["planner_output"])
    if 'raw_response' in state["nppes_output"]:
        raw_response = state["nppes_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("NPPES Output:", state["nppes_output"])
    return state

def private_node(state: SwarmState) -> SwarmState:
    private = PrivateClinicAgent()
    state["private_output"] = private.process(state["planner_output"])
    if 'raw_response' in state["private_output"]:
        raw_response = state["private_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Private node Output:", state["private_output"])
    return state

def planner_supervisor_node(state: SwarmState) -> SwarmState:
    sup = PlannerSupervisor()
    state["planner_sup_output"] = sup.validate_and_output(state["planner_output"])
    if 'raw_response' in state["planner_sup_output"]:
        raw_response = state["planner_sup_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Planner Supervisor Output:", state["planner_sup_output"])
    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "planner_supervisor",
        "output": state["planner_sup_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state

def candidate_extractor_node(state: SwarmState) -> SwarmState:
    ext = CandidateExtractorAgent()
    state["candidate_output"] = ext.process(state["planner_sup_output"])
    if 'raw_response' in state["candidate_output"]:
        raw_response = state["candidate_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Candidate Extractor Output:", state["candidate_output"])
    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "candidate_extractor",
        "output": state["candidate_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state

def candidate_supervisor_node(state: SwarmState) -> SwarmState:
    sup = CandidateExtractorSupervisor()
    state["candidate_sup_output"] = sup.validate_and_output(state["candidate_output"])
    if 'raw_response' in state["candidate_sup_output"]:
        raw_response = state["candidate_sup_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Candidate Supervisor Output:", state["candidate_sup_output"])
    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "candidate_supervisor",
        "output": state["candidate_sup_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state

def selector_node(state: SwarmState) -> SwarmState:
    sel = SelectorAgent()
    state["selector_output"] = sel.process(state["candidate_sup_output"])
    if 'raw_response' in state["selector_output"]:
        raw_response = state["selector_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Selector Output:", state["selector_output"])
    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "selector",
        "output": state["selector_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state

def selector_supervisor_node(state: SwarmState) -> SwarmState:
    sup = SelectorSupervisor()
    state["selector_sup_output"] = sup.validate_and_output(state["selector_output"])
    if 'raw_response' in state["selector_sup_output"]:
        raw_response = state["selector_sup_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Selector Supervisor Output:", state["selector_sup_output"])
    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "selector_supervisor",
        "output": state["selector_sup_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state

def enricher_node(state: SwarmState) -> SwarmState:
    enr = EnricherAgent()
    state["enricher_output"] = enr.process(state["selector_sup_output"])
    if 'raw_response' in state["enricher_output"]:
        raw_response = state["enricher_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Enricher Output:", state["enricher_output"])
    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "enricher",
        "output": state["enricher_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state

def enricher_supervisor_node(state: SwarmState) -> SwarmState:
    sup = EnricherSupervisor()
    state["enricher_sup_output"] = sup.validate_and_output(state)
    if 'raw_response' in state["enricher_sup_output"]:
        raw_response = state["enricher_sup_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Enricher Supervisor Output:", state["enricher_sup_output"])

    # Set final_output directly from enricher_sup_output since validator is incomplete
    state["final_output"] = state["enricher_sup_output"]

    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "enricher_supervisor",
        "output": state["enricher_sup_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state

def validator_node(state: SwarmState) -> SwarmState:
    val = ValidatorAgent()
    state["validator_output"] = val.process(state["enricher_sup_output"])
    if 'raw_response' in state["validator_output"]:
        raw_response = state["validator_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Validator Output:", state["validator_output"])
    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "validator",
        "output": state["validator_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state

def validator_supervisor_node(state: SwarmState) -> SwarmState:
    sup = ValidatorSupervisor()
    state["final_output"] = sup.validate_and_output(state["validator_output"])
    if 'raw_response' in state["final_output"]:
        raw_response = state["final_output"]["raw_response"]
        if isinstance(raw_response, dict) and 'messages' in raw_response:
            print("Messages:", raw_response["messages"])
        else:
            print("Raw Response:", raw_response)
    print("Final Output:", state["final_output"])
    # Add to short-term memory
    if "short_term_memory" not in state:
        state["short_term_memory"] = []
    state["short_term_memory"].append({
        "agent": "validator_supervisor",
        "output": state["final_output"],
        "timestamp": str(__import__('datetime').datetime.now())
    })
    return state



# Build the workflow
workflow = StateGraph(SwarmState)

# Add nodes
workflow.add_node("planner", planner_node)
workflow.add_node("nppes", nppes_node)
workflow.add_node("private", private_node)
workflow.add_node("planner_sup", planner_supervisor_node)
workflow.add_node("candidate_extractor", candidate_extractor_node)
workflow.add_node("candidate_sup", candidate_supervisor_node)
workflow.add_node("selector", selector_node)
workflow.add_node("selector_sup", selector_supervisor_node)
workflow.add_node("enricher", enricher_node)
workflow.add_node("enricher_sup", enricher_supervisor_node)
workflow.add_node("validator", validator_node)
workflow.add_node("validator_sup", validator_supervisor_node)

# Define routing function for planner
def route_planner(state: SwarmState):
    planner_output = state.get("planner_output", {})
    status = planner_output.get("status")

    if status == "search_query_prepared":
        # Send to both agents to get their results
        return ["nppes", "private"]
    elif status == "results_combined":
        # Results combined - go to planner supervisor for validation
        return ["planner_sup"]
    else:
        # Error or unexpected status
        return ["__end__"]

# Define edges
workflow.add_edge(START, "planner")
workflow.add_conditional_edges("planner", route_planner)
workflow.add_edge("nppes", "planner")
workflow.add_edge("private", "planner")
workflow.add_edge("planner_sup", "candidate_extractor")
workflow.add_edge("candidate_extractor", "candidate_sup")
workflow.add_edge("candidate_sup", "selector")
workflow.add_edge("selector", "selector_sup")
workflow.add_edge("selector_sup", "enricher")
workflow.add_edge("enricher", "enricher_sup")
workflow.add_edge("enricher_sup", END)  # Skip validator stage, go directly to END

# Compile the graph
app = workflow.compile()
