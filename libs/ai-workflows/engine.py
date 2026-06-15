import sys
from typing import Dict, Any, List, Optional

sys.path.append(".")
sys.path.append("./libs/ai-workflows")
from states import ContentWorkflowState, STATE_TRANSITIONS, INITIAL_STATE
from libs.llm.agents.core import create_agent

# HUMAN_REVIEW is intentionally absent — no agent runs automatically for that state.
STATE_AGENT_MAP: Dict[ContentWorkflowState, str] = {
    ContentWorkflowState.PLANNING: "planner",
    ContentWorkflowState.DRAFTING: "writer",
    ContentWorkflowState.REVIEW: "reviewer",
    ContentWorkflowState.REVISION: "writer",
}


class WorkflowEngine:
    """Manages the lifecycle of a content workflow, including state transitions and agent execution.

    Validates transitions against STATE_TRANSITIONS, automatically runs the mapped LLM agent
    for each active state, and transitions to FAILED with structured error details on agent failure.
    HUMAN_REVIEW is a pause point — no agent runs until submit_human_review() is called.
    """

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

    def is_awaiting_human_review(self) -> bool:
        return self.current_state == ContentWorkflowState.HUMAN_REVIEW

    def execute_agent_action(self, user_input: str) -> Optional[str]:
        """Run the agent mapped to the current state and store its output in metadata.

        Automatically calls fail() if the agent raises or returns None.
        Returns the agent's text output, or None if the state has no mapped agent or the agent fails.
        """
        if self.is_awaiting_human_review():
            return None  # Paused — resume via submit_human_review()
        agent_name = STATE_AGENT_MAP.get(self.current_state)
        if not agent_name or not self.openai_client:
            return None

        failed_at = self.current_state.value
        try:
            agent = create_agent(agent_name, self.openai_client, self.llm_model)
            output = agent.run(user_input, context=self.metadata)
        except Exception as e:
            self.fail(
                reason=f"Agent '{agent_name}' raised an exception in state '{failed_at}': {e}"
            )
            return None

        if output is None:
            self.fail(
                reason=f"Agent '{agent_name}' returned no output in state '{failed_at}' after exhausting retries."
            )
            return None

        self.metadata[f"{self.current_state.value.lower()}_output"] = output
        return output

    def submit_human_review(self, approved: bool, feedback: str = "") -> None:
        """Record a human reviewer's decision and transition accordingly.

        approved=True  → COMPLETED; approved=False → REVISION.
        Raises ValueError if the workflow is not in HUMAN_REVIEW state.
        """
        if not self.is_awaiting_human_review():
            raise ValueError(
                f"Cannot submit human review: workflow is in '{self.current_state.value}', not 'HUMAN_REVIEW'."
            )
        self.metadata["human_review_feedback"] = feedback
        if approved:
            self.transition(
                ContentWorkflowState.COMPLETED,
                reason=f"Approved by human reviewer. {feedback}".strip(),
            )
        else:
            self.transition(
                ContentWorkflowState.REVISION,
                reason=f"Returned for revision. {feedback}".strip(),
            )

    def fail(self, reason: str = "Unspecified error") -> None:
        self.metadata["error"] = {"failed_at_state": self.current_state.value, "reason": reason}
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
            "awaiting_human_review": self.is_awaiting_human_review(),
            "history": self.history,
            "metadata": self.metadata,
            "agent_output": self.metadata.get(output_key),
            "error": self.metadata.get("error"),
        }
