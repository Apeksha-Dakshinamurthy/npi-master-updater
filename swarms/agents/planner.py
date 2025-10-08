from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..prompts.planner_prompt import PLANNER_AGENT_PROMPT
from ..memory import get_memory_instance
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

class PlannerAgent:
    """
    PlannerAgent coordinates searches across NPPES and private clinic agents.
    Phase 1: Prepares search query for subordinate agents
    Phase 2: Combines and refines results from both agents using LLM
    """

    def __init__(self):
        self._llm = None
        self._agent = None
        self.memory = get_memory_instance()

    @property
    def llm(self):
        if self._llm is None:
            self._llm = ChatOpenAI(model="gpt-5-mini")
        return self._llm

    @property
    def agent(self):
        if self._agent is None:
            self._agent = create_react_agent(
                model=self.llm,
                tools=[],
                prompt=PLANNER_AGENT_PROMPT
            )
        return self._agent

    def _preprocess_input(self, first_name: str, middle_name: str, last_name: str, classification: str, npi_number: str) -> str:
        """Create search query from physician details"""
        name_parts = [part for part in [first_name, middle_name, last_name] if part]
        search_query = " ".join(name_parts)
        if classification:
            search_query += f" {classification}"
        if npi_number:
            search_query += f" NPI {npi_number}"
        return search_query.strip()

    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON from LLM response"""
        import re
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        return json_match.group(0) if json_match else content

    def process(self, state: dict) -> dict:
        """
        Two-phase process:
        1. If no agent results yet: prepare search query for agents
        2. If both agents done: combine and refine their results
        """
        input_data = state.get("input_data", {})
        nppes_output = state.get("nppes_output")
        private_output = state.get("private_output")

        # Phase 1: Prepare search query if agents haven't run yet
        if not nppes_output or not private_output:
            search_query = self._preprocess_input(
                input_data.get("first_name", ""),
                input_data.get("middle_name", ""),
                input_data.get("last_name", ""),
                input_data.get("classification", ""),
                input_data.get("npi_number", "")
            )

            return {
                "search_query_input": search_query,
                "input": input_data,
                "status": "search_query_prepared"
            }

        # Phase 2: Combine results from both agents
        nppes_results = nppes_output.get("nppes_results", [])
        private_results = private_output.get("clinic_results", [])

        # Results are already strings from the agents, but ensure they're properly formatted
        nppes_results_safe = nppes_results if isinstance(nppes_results, list) else []
        private_results_safe = private_results if isinstance(private_results, list) else []

        # Prepare input for LLM using planner prompt
        prompt_input = {
            "Physician_first_name": input_data.get("first_name", ""),
            "Physician_middle_name": input_data.get("middle_name", ""),
            "Physician_last_name": input_data.get("last_name", ""),
            "NPI_number": input_data.get("npi_number", ""),
            "PRIMARY_AFFILIATION_NAME": input_data.get("primary_affiliation_name", ""),
            "nppes_results": nppes_results_safe,
            "private_results": private_results_safe
        }

        response = None
        try:
            # Format input for LLM
            prompt_text = f"""
Physician Information:
- First Name: {prompt_input['Physician_first_name']}
- Middle Name: {prompt_input['Physician_middle_name']}
- Last Name: {prompt_input['Physician_last_name']}
- NPI Number: {prompt_input['NPI_number']}
- Primary Affiliation Name: {prompt_input['PRIMARY_AFFILIATION_NAME']}

NPPES Results:
{json.dumps(prompt_input['nppes_results'], indent=2)}

Private Clinic Results:
{json.dumps(prompt_input['private_results'], indent=2)}
"""

            response = self.agent.invoke({"messages": [{"role": "user", "content": prompt_text}]})
            content = response['messages'][-1].content.strip()

            # Extract and parse JSON
            json_content = self._extract_json_from_response(content)
            output = json.loads(json_content)
            output["status"] = "results_combined"
            #print("Planner combined output:", output)
            return output

        except Exception as e:
            logger.error("Error in planner processing: %s", e)
            raw_response = "No response"
            if response and 'messages' in response:
                try:
                    last_message = response['messages'][-1]
                    if hasattr(last_message, 'content'):
                        raw_response = last_message.content
                except Exception:
                    raw_response = "Error extracting response"

            return {
                "error": str(e),
                "status": "error",
                "raw_response": raw_response
            }
