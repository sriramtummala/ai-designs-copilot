import sys
from typing import Dict, Any, List, Optional

sys.path.append("./libs/ai-workflows")
from states import ContentWorkflowState, STATE_TRANSITIONS, INITIAL_STATE


class WorkflowEngine:
    def __init__(self, workflow_id: str, metadata: Optional[Dict[str, Any]] = None):
        self.workflow_id = workflow_id
        self.current_state: ContentWorkflowState = INITIAL_STATE
        self.metadata: Dict[str, Any] = metadata or {}
        self.history: List[Dict[str, Any]] = [
            {"state": self.current_state.value, "reason": "Workflow initialized"}
        ]

    def can_transition(self, new_state: ContentWorkflowState) -> bool:
        return new_state in STATE_TRANSITIONS.get(self.current_state, [])

    def transition(self, new_state: ContentWorkflowState, reason: str = "") -> bool:
        if not self.can_transition(new_state):
            raise ValueError(
                f"Invalid transition: {self.current_state.value} → {new_state.value}. "
                f"Allowed: {[s.value for s in STATE_TRANSITIONS.get(self.current_state, [])]}"
            )
        self.current_state = new_state
        self.history.append({"state": new_state.value, "reason": reason})
        return True

    def fail(self, reason: str = "Unspecified error") -> None:
        self.current_state = ContentWorkflowState.FAILED
        self.history.append({"state": ContentWorkflowState.FAILED.value, "reason": reason})

    def is_terminal(self) -> bool:
        return self.current_state in (ContentWorkflowState.COMPLETED, ContentWorkflowState.FAILED)

    def get_status(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "current_state": self.current_state.value,
            "is_terminal": self.is_terminal(),
            "history": self.history,
            "metadata": self.metadata,
        }
