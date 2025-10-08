from typing import Annotated

from langchain_core.tools import tool, BaseTool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState

def create_custom_handoff_tool(*, agent_name: str, name: str | None = None, description: str | None = None) -> BaseTool:
    if name is None:
        name = f"handoff_to_{agent_name}"
    if description is None:
        description = f"Transfer control to {agent_name}"

    @tool(name, description=description)
    def handoff_to_agent(
        task_description: Annotated[str, "Detailed description of what the next agent should do, including all of the relevant context."],
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        tool_message = ToolMessage(
            content=f"Successfully transferred to {agent_name}",
            name=name,
            tool_call_id=tool_call_id,
        )
        messages = state["messages"]
        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update={
                "messages": messages + [tool_message],
                "active_agent": agent_name,
                "task_description": task_description,
            },
        )

    return handoff_to_agent
