from typing import List, Dict, Any, Optional
from openai import OpenAI
import json

from libs.llm.tools import AVAILABLE_TOOLS
from libs.llm.tool_functions import TOOL_FUNCTIONS
from libs.llm.agents.roles import AGENT_PROMPTS


class BaseAgent:
    def __init__(self, name: str, system_prompt: str, openai_client: OpenAI, llm_model: str):
        self.name = name
        self.system_prompt = system_prompt
        self.openai_client = openai_client
        self.llm_model = llm_model
        self.conversation_history: List[Any] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _call_llm(self, messages: List[Any], tools: Optional[List[Dict[str, Any]]] = None):
        kwargs: Dict[str, Any] = dict(
            model=self.llm_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
        )
        if tools:
            kwargs.update(tools=tools, tool_choice="auto")
        try:
            return self.openai_client.chat.completions.create(**kwargs).choices[0].message
        except Exception as e:
            print(f"Agent '{self.name}' LLM error: {e}")
            return None

    def run(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        self.conversation_history.append({"role": "user", "content": user_input})
        if context:
            self.conversation_history.append(
                {"role": "system", "content": f"Additional context: {json.dumps(context)}"}
            )

        while True:
            msg = self._call_llm(self.conversation_history, tools=AVAILABLE_TOOLS)
            if msg is None:
                return ""
            self.conversation_history.append(msg)

            if not msg.tool_calls:
                return msg.content or ""

            for tc in msg.tool_calls:
                func = TOOL_FUNCTIONS.get(tc.function.name)
                args = json.loads(tc.function.arguments)
                result = func(**args) if func else {"error": f"Unknown tool: {tc.function.name}"}
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tc.function.name,
                    "content": json.dumps(result),
                })


class PlannerAgent(BaseAgent):
    def __init__(self, openai_client: OpenAI, llm_model: str):
        super().__init__("Planner", AGENT_PROMPTS["planner"], openai_client, llm_model)


class ResearcherAgent(BaseAgent):
    def __init__(self, openai_client: OpenAI, llm_model: str):
        super().__init__("Researcher", AGENT_PROMPTS["researcher"], openai_client, llm_model)


class WriterAgent(BaseAgent):
    def __init__(self, openai_client: OpenAI, llm_model: str):
        super().__init__("Writer", AGENT_PROMPTS["writer"], openai_client, llm_model)


class ReviewerAgent(BaseAgent):
    def __init__(self, openai_client: OpenAI, llm_model: str):
        super().__init__("Reviewer", AGENT_PROMPTS["reviewer"], openai_client, llm_model)


_AGENT_REGISTRY: Dict[str, type] = {
    "planner": PlannerAgent,
    "researcher": ResearcherAgent,
    "writer": WriterAgent,
    "reviewer": ReviewerAgent,
}


def create_agent(agent_name: str, openai_client: OpenAI, llm_model: str) -> BaseAgent:
    cls = _AGENT_REGISTRY.get(agent_name)
    if not cls:
        raise ValueError(f"Unknown agent: {agent_name!r}. Available: {list(_AGENT_REGISTRY)}")
    return cls(openai_client, llm_model)
