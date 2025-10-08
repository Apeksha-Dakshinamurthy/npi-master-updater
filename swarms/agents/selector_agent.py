from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..prompts.selector_prompt import SELECTOR_AGENT_PROMPT
import json
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)

class SelectorAgent:
    """
    SelectorAgent applies hierarchy and tie-breaker rules on candidates,
    compares and selects the best candidate(s) between web candidates and master table entries.
    """

    def __init__(self):
        # Lazy initialization - only create LLM and agent when needed
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
                prompt=SELECTOR_AGENT_PROMPT
            )
        return self._agent

    def _extract_json_from_response(self, content: str) -> str:
        """
        Extracts JSON from the LLM response, handling cases where it's wrapped in markdown or has extra text.
        """
        import re
        # Remove markdown code blocks if present
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        # Find JSON object
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return content

    def process(self, candidate_supervisor_output: dict) -> dict:
        """
        Process the validated candidate data to apply hierarchy and select the best candidates.

        Args:
            candidate_supervisor_output (dict): Validated output from candidate_extractor_supervisor

        Returns:
            dict: Selected candidates with hierarchy and tie-breaker logic applied
        """
        try:
            # Format the input for the LLM
            prompt_text = f"""
Validated Candidate Data:
{json.dumps(candidate_supervisor_output, indent=2)}

Apply hierarchy and tie-breaker rules:
1. Prioritize tier_1 candidates over tier_2 and tier_3
2. For same tier, prefer candidates with complete address and phone information
3. For same tier and completeness, prefer most recent page_date
4. Select top 3 candidates maximum

Output the selected candidates in the specified JSON structure.
"""

            response = self.agent.invoke({"messages": [{"role": "user", "content": prompt_text}]})
            content = response['messages'][-1].content.strip()

            # Extract and parse JSON
            json_content = self._extract_json_from_response(content)
            output = json.loads(json_content)
            output["status"] = "candidates_selected"
            #print("Selector output:", output)
            return output

        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response as JSON: %s", e)
            return {
                "error": "Failed to parse LLM response",
                "raw_response": content if 'content' in locals() else "No response",
                "status": "error"
            }
        except Exception as e:
            logger.error("Unexpected error in candidate selection: %s", e)
            return {
                "error": str(e),
                "status": "error",
                "raw_response": content if 'content' in locals() else "No response"
            }
