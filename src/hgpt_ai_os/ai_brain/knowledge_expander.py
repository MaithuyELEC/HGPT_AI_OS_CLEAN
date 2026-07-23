from typing import List

DEFAULT_KNOWLEDGE = [
    "Root Cause Analysis",
    "Safety",
    "Best Practices",
    "Common Failure Modes",
    "Inspection",
    "Maintenance",
    "Troubleshooting",
    "Quality Control"
]

DOMAIN_KEYWORDS = {
    "motor": [
        "Bearing",
        "Insulation",
        "Current imbalance",
        "Phase loss",
        "Thermal overload",
        "Ventilation",
        "Vibration",
        "Alignment",
        "Lubrication",
        "Infrared inspection"
    ],
    "crane": [
        "Wire rope",
        "Brake",
        "Hook",
        "Limit switch",
        "Gearbox",
        "Motor",
        "Reducer",
        "Drum",
        "Load test",
        "ISO 4309"
    ],
    "welding": [
        "WPS",
        "PQR",
        "WPQ",
        "AWS D1.1",
        "UT",
        "MT",
        "PT",
        "Distortion",
        "Heat input",
        "Penetration"
    ]
}

def expand(topic: str) -> List[str]:
    topic_lower = topic.lower()

    knowledge = list(DEFAULT_KNOWLEDGE)

    for key, values in DOMAIN_KEYWORDS.items():
        if key in topic_lower:
            knowledge.extend(values)

    return sorted(set(knowledge))
