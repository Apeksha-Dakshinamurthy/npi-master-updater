from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..prompts.enricher_supervisor_prompt import ENRICHER_SUPERVISOR_PROMPT
from ..tools.tavily_tool import get_tavily_tool
import json
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)

class EnricherSupervisor:
    """
    EnricherSupervisor receives queries from enricher agent, performs searches, and extracts enrichment data.
    """

    def __init__(self):
        # Lazy initialization - only create LLM and agent when needed
        self._llm = None
        self._agent = None
        self._tavily_tool = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = ChatOpenAI(model="gpt-5-mini")
        return self._llm

    @property
    def tavily_tool(self):
        if self._tavily_tool is None:
            self._tavily_tool = get_tavily_tool(max_results=5)
        return self._tavily_tool

    @property
    def agent(self):
        if self._agent is None:
            self._agent = create_react_agent(
                model=self.llm,
                tools=[self.tavily_tool],
                prompt=ENRICHER_SUPERVISOR_PROMPT
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

        # Try to find JSON object with better regex
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            # Clean up common JSON issues
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
            return json_str

        return content

    def validate_and_output(self, state: dict) -> dict:
        """Execute enrichment queries and extract data"""
        try:
            # Get enricher queries and selector supervisor output
            enricher_output = state.get("enricher_output", {})
            selector_sup_output = state.get("selector_sup_output", {})

            # Combine context for the agent
            context = {
                "enricher_queries": enricher_output,
                "selector_supervisor_output": selector_sup_output
            }

            response = self.agent.invoke({"messages": [{"role": "user", "content": json.dumps(context)}]})
            content = response['messages'][-1].content.strip()
            json_content = self._extract_json_from_response(content)
            output = json.loads(json_content)
            #print("EnricherSupervisor output:", output)
            return output
        except Exception as e:
            print(f"EnricherSupervisor error: {e}")
            return {
                "error": str(e),
                "status": "supervisor_error",
                "raw_response": response['messages'][-1].content if 'response' in locals() and response else "No response"
            }
