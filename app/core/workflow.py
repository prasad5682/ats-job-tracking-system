# app/core/workflow.py

VALID_STAGES = [
    "Applied",
    "Screening",
    "Interview",
    "Offer",
    "Hired",
    "Rejected"
]

ALLOWED_TRANSITIONS = {
    "Applied": ["Screening", "Rejected"],
    "Screening": ["Interview", "Rejected"],
    "Interview": ["Offer", "Rejected"],
    "Offer": ["Hired", "Rejected"],
    "Hired": [],
    "Rejected": []
}

def is_valid_transition(current_stage: str, next_stage: str) -> bool:
    # Validate both stages exist
    if current_stage not in VALID_STAGES or next_stage not in VALID_STAGES:
        return False
    # Check allowed transitions
    return next_stage in ALLOWED_TRANSITIONS.get(current_stage, [])

def get_allowed_transitions(stage: str):
    return ALLOWED_TRANSITIONS.get(stage, [])
