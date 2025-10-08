from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..tools.tavily_tool import get_tavily_tool
from ..prompts.enricher_prompt import ENRICHER_AGENT_PROMPT
import json
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)

class EnricherAgent:
    """
    EnricherAgent receives input from selector supervisor and performs enrichment prompt.
    Simplified to match other agents' structure without additional extraction of selected candidates or physician details.
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
            self.tavily_tool = get_tavily_tool()
            self._agent = create_react_agent(
                model=self.llm,
                tools=[self.tavily_tool],
                prompt=ENRICHER_AGENT_PROMPT
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

    def process(self, selector_supervisor_output: dict) -> dict:
        """
        Process method that receives input from selector supervisor and performs enrichment prompt.

        Args:
            selector_supervisor_output (dict): Output from selector supervisor

        Returns:
            dict: Enricher output as JSON
        """
        try:
            response = self.agent.invoke({"messages": [{"role": "user", "content": json.dumps(selector_supervisor_output)}]})
            content = response['messages'][-1].content.strip()
            json_content = self._extract_json_from_response(content)
            output = json.loads(json_content)
            print("Enricher output:", output)
            return output
        except Exception as e:
            logger.error("Error in enricher agent processing: %s", e)
            return {
                "error": str(e),
                "status": "error",
                "raw_response": content if 'content' in locals() else "No response"
            }
