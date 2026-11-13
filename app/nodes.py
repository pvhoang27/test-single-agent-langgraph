from langchain_core.messages import SystemMessage

from app.config import create_llm
from app.prompts import system_prompt
from app.state import AgentState
from app.tools import TOOLS


llm_with_tools = create_llm().bind_tools(TOOLS)


def agent_node(state: AgentState) -> dict:
    response = llm_with_tools.invoke(
        [SystemMessage(content=system_prompt()), *state["messages"]]
    )
    return {"messages": [response]}
