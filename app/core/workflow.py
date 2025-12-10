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
    return next_stage in ALLOWED_TRANSITIONS.get(current_stage, [])
