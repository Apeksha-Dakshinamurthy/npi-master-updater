from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..prompts.candidate_extractor_prompt import CANDIDATE_EXTRACTOR_PROMPT
import json
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)

class CandidateExtractorAgent:
    """
    CandidateExtractorAgent processes validated planner results to extract and categorize
    candidate affiliations from search results.
    """

    def __init__(self):
        self._llm = None
        self._agent = None

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
                prompt=CANDIDATE_EXTRACTOR_PROMPT
            )
        return self._agent

    def _extract_json_from_response(self, content: str) -> str:
        """
        Extracts JSON from the LLM response, handling cases where it's wrapped in markdown or with extra text.
        """
        import re
        # Remove markdown code blocks if present
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        # Find the outermost JSON object
        brace_count = 0
        start_idx = -1
        for i, char in enumerate(content):
            if char == '{':
                if brace_count == 0:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    return content[start_idx:i+1]
        # Fallback to simple regex if brace matching fails
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return content

    def process(self, planner_supervisor_output: dict) -> dict:
        """
        Process the validated planner output to extract candidate affiliations.

        Args:
            planner_supervisor_output (dict): Validated output from planner_supervisor

        Returns:
            dict: Extracted candidates with categorization and metadata
        """
        try:
            # Format the input for the LLM
            prompt_text = f"""
Physician Information (RETAIN EXACTLY AS PROVIDED):
- First Name: {planner_supervisor_output.get('Physician_first_name', '')}
- Middle Name: {planner_supervisor_output.get('Physician_middle_name', '')}
- Last Name: {planner_supervisor_output.get('Physician_last_name', '')}
- NPI Number: {planner_supervisor_output.get('NPI_number', '')}
- Primary Affiliation Name: {planner_supervisor_output.get('PRIMARY_AFFILIATION_NAME', '')}

Hit Results (retain exact array from input):
{json.dumps(planner_supervisor_output.get('hit_results', []), indent=2)}

Source URLs:
{json.dumps(planner_supervisor_output.get('affiliations_source_urls', []), indent=2)}

Processing Notes from Planner:
{planner_supervisor_output.get('notes', 'No additional notes')}

IMPORTANT: You MUST retain the physician information and hit_results exactly as provided above in your output JSON.
For any missing information in candidates, use "missing" as the value.
Extract candidate affiliations and format the output according to the specified JSON structure.
"""

            response = self.agent.invoke({"messages": [{"role": "user", "content": prompt_text}]})
            content = response['messages'][-1].content.strip()

            # Extract and parse JSON
            json_content = self._extract_json_from_response(content)
            output = json.loads(json_content)
            output["status"] = "candidates_extracted"
            #print("CandidateExtractor output:", output)
            return output

        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response as JSON: %s", e)
            return {
                "error": "Failed to parse LLM response",
                "raw_response": content if 'content' in locals() else "No response",
                "status": "error"
            }
        except Exception as e:
            logger.error("Unexpected error in candidate extraction: %s", e)
            return {
                "error": str(e),
                "status": "error",
                "raw_response": content if 'content' in locals() else "No response"
            }
