from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..tools.tavily_tool import get_tavily_tool
from ..prompts.privateclinic_prompt import PRIVATECLINIC_AGENT_PROMPT

class PrivateClinicAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5-mini")
        self.tavily_tool = get_tavily_tool()
        self.agent = create_react_agent(
            model=self.llm,
            tools=[self.tavily_tool],
            prompt=PRIVATECLINIC_AGENT_PROMPT
        )

    def process(self, input_data: dict) -> dict:
        search_query_input = input_data.get("search_query_input", "")
        query = f"Search private clinics and hospitals for provider: {search_query_input}"
        result = self.agent.invoke({"messages": [{"role": "user", "content": query}]})

        # Extract the actual content from the LangChain response
        clinic_results = []
        if result and 'messages' in result:
            for message in result['messages']:
                content = None
                if hasattr(message, 'content'):
                    content = message.content
                elif isinstance(message, dict) and 'content' in message:
                    content = message['content']

                # Handle different content types
                if content:
                    if isinstance(content, str) and content.strip():
                        clinic_results.append(content)
                    elif isinstance(content, list):
                        # Convert list to string
                        content_str = str(content)
                        if content_str.strip() and content_str != '[]':
                            clinic_results.append(content_str)
                    else:
                        # Convert other types to string
                        content_str = str(content)
                        if content_str.strip():
                            clinic_results.append(content_str)

        return {"clinic_results": clinic_results, "input": input_data}
