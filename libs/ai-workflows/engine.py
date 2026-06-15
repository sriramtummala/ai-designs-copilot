import sys
from typing import Dict, Any, List, Optional

sys.path.append(".")
sys.path.append("./libs/ai-workflows")
from states import ContentWorkflowState, STATE_TRANSITIONS, INITIAL_STATE
from libs.llm.agents.core import create_agent

# Maps each active workflow state to the agent responsible for that phase
STATE_AGENT_MAP: Dict[ContentWorkflowState, str] = {
    ContentWorkflowState.PLANNING: "planner",
    ContentWorkflowState.DRAFTING: "writer",
    ContentWorkflowState.REVIEW: "reviewer",
    ContentWorkflowState.REVISION: "writer",
}


class WorkflowEngine:
    def __init__(
        self,
        workflow_id: str,
        openai_client,
        llm_model: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.workflow_id = workflow_id
        self.openai_client = openai_client
        self.llm_model = llm_model
        self.current_state: ContentWorkflowState = INITIAL_STATE
        self.metadata: Dict[str, Any] = metadata or {}
        self.history: List[Dict[str, Any]] = [
            {"state": self.current_state.value, "reason": "Workflow initialized"}
        ]

    def can_transition(self, new_state: ContentWorkflowState) -> bool:
        return new_state in STATE_TRANSITIONS.get(self.current_state, [])

    def transition(self, new_state: ContentWorkflowState, reason: str = "") -> None:
        if not self.can_transition(new_state):
            raise ValueError(
                f"Invalid transition: {self.current_state.value} → {new_state.value}. "
                f"Allowed: {[s.value for s in STATE_TRANSITIONS.get(self.current_state, [])]}"
            )
        self.current_state = new_state
        self.history.append({"state": new_state.value, "reason": reason})

    def execute_agent_action(self, user_input: str) -> Optional[str]:
        agent_name = STATE_AGENT_MAP.get(self.current_state)
        if not agent_name or not self.openai_client:
            return None
        agent = create_agent(agent_name, self.openai_client, self.llm_model)
        output = agent.run(user_input, context=self.metadata)
        self.metadata[f"{self.current_state.value.lower()}_output"] = output
        return output

    def fail(self, reason: str = "Unspecified error") -> None:
        self.current_state = ContentWorkflowState.FAILED
        self.history.append({"state": ContentWorkflowState.FAILED.value, "reason": reason})

    def is_terminal(self) -> bool:
        return self.current_state in (ContentWorkflowState.COMPLETED, ContentWorkflowState.FAILED)

    def get_status(self) -> Dict[str, Any]:
        output_key = f"{self.current_state.value.lower()}_output"
        return {
            "workflow_id": self.workflow_id,
            "current_state": self.current_state.value,
            "is_terminal": self.is_terminal(),
            "history": self.history,
            "metadata": self.metadata,
            "agent_output": self.metadata.get(output_key),
        }
