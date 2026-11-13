from typing import Literal

from langchain_core.messages import AIMessage

from app.state import AgentState


def route_after_agent(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "__end__"
