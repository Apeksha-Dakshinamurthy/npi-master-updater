from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..prompts.candidate_extractor_supervisor_prompt import CANDIDATE_EXTRACTOR_SUPERVISOR_PROMPT
import json
import re

class CandidateExtractorSupervisor:
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
                prompt=CANDIDATE_EXTRACTOR_SUPERVISOR_PROMPT
            )
        return self._agent

    def _extract_json_from_response(self, content: str) -> str:
        """
        Extracts JSON from the LLM response, handling cases where it's wrapped in markdown or has extra text.
        """
        # Remove markdown code blocks if present
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        # Find JSON object
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json_match.group(0)
        return content

    def validate_and_output(self, extractor_output: dict) -> dict:
        """Validate candidate extractor output and return corrected JSON"""
        try:
            response = self.agent.invoke({"messages": [{"role": "user", "content": json.dumps(extractor_output)}]})
            content = response['messages'][-1].content.strip()
            json_content = self._extract_json_from_response(content)
            output = json.loads(json_content)
            #print("CandidateExtractorSupervisor validated output:", output)
            return output
        except Exception as e:
            print(f"CandidateExtractorSupervisor error: {e}")
            return {
                "error": str(e),
                "status": "supervisor_error",
                "raw_response": response['messages'][-1].content if response else "No response"
            }
