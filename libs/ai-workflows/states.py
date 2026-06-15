from enum import Enum

class ContentWorkflowState(str, Enum):
    INITIALIZED = "INITIALIZED"
    PLANNING = "PLANNING"
    DRAFTING = "DRAFTING"
    REVIEW = "REVIEW"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    REVISION = "REVISION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

STATE_TRANSITIONS = {
    ContentWorkflowState.INITIALIZED:  [ContentWorkflowState.PLANNING, ContentWorkflowState.FAILED],
    ContentWorkflowState.PLANNING:     [ContentWorkflowState.DRAFTING, ContentWorkflowState.FAILED],
    ContentWorkflowState.DRAFTING:     [ContentWorkflowState.REVIEW, ContentWorkflowState.REVISION, ContentWorkflowState.FAILED],
    ContentWorkflowState.REVIEW:       [ContentWorkflowState.HUMAN_REVIEW, ContentWorkflowState.REVISION, ContentWorkflowState.FAILED],
    ContentWorkflowState.HUMAN_REVIEW: [ContentWorkflowState.COMPLETED, ContentWorkflowState.REVISION, ContentWorkflowState.FAILED],
    ContentWorkflowState.REVISION:     [ContentWorkflowState.DRAFTING, ContentWorkflowState.REVIEW, ContentWorkflowState.FAILED],
    ContentWorkflowState.COMPLETED:    [],
    ContentWorkflowState.FAILED:       [],
}

INITIAL_STATE = ContentWorkflowState.INITIALIZED
