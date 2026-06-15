from enum import Enum

class ContentWorkflowState(str, Enum):
    INITIALIZED = "INITIALIZED"
    PLANNING = "PLANNING"
    DRAFTING = "DRAFTING"
    REVIEW = "REVIEW"
    REVISION = "REVISION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
 
# Define allowed state transitions
# Key: current state, Value: list of allowed next states
STATE_TRANSITIONS = {
    ContentWorkflowState.INITIALIZED: [ContentWorkflowState.PLANNING, ContentWorkflowState.FAILED],
    ContentWorkflowState.PLANNING: [ContentWorkflowState.DRAFTING, ContentWorkflowState.FAILED],
    ContentWorkflowState.DRAFTING: [ContentWorkflowState.REVIEW, ContentWorkflowState.REVISION, ContentWorkflowState.FAILED],
    ContentWorkflowState.REVIEW: [ContentWorkflowState.COMPLETED, ContentWorkflowState.REVISION, ContentWorkflowState.FAILED],
    ContentWorkflowState.REVISION: [ContentWorkflowState.DRAFTING, ContentWorkflowState.REVIEW, ContentWorkflowState.FAILED],
    ContentWorkflowState.COMPLETED: [], # Terminal state
    ContentWorkflowState.FAILED: []    # Terminal state
}
 
INITIAL_STATE = ContentWorkflowState.INITIALIZED
