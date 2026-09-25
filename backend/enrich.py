"""Neighbourhood lifestyle scores for each locality (demo).
Each score is 0-100. Overall is average.
"""

LIFESTYLE_SCORES = {
    "loc-ajmer-road": {
        "walkability": 68, "schools": 72, "hospitals": 65, "connectivity": 82, "safety": 74,
        "notes": "Well-connected via NH-48 and metro extension; multiple schools and hospitals within 3 km.",
    },
    "loc-jagatpura": {
        "walkability": 76, "schools": 88, "hospitals": 78, "connectivity": 85, "safety": 82,
        "notes": "Strong social infrastructure with premier schools (JECRC, Poornima) and multi-speciality hospitals.",
    },
    "loc-tonk-road": {
        "walkability": 71, "schools": 80, "hospitals": 85, "connectivity": 90, "safety": 76,
        "notes": "Central arterial road; excellent hospital ecosystem including Fortescue and Jaipur Hospital nearby.",
    },
    "loc-vaishali-nagar": {
        "walkability": 84, "schools": 90, "hospitals": 82, "connectivity": 78, "safety": 88,
        "notes": "Planned locality with wide roads, premium schools and family-first amenities.",
    },
    "loc-mansarovar": {
        "walkability": 82, "schools": 86, "hospitals": 80, "connectivity": 84, "safety": 85,
        "notes": "One of the largest planned townships in Rajasthan with strong self-contained infrastructure.",
    },
    "loc-sikar-road": {
        "walkability": 58, "schools": 62, "hospitals": 55, "connectivity": 72, "safety": 68,
        "notes": "Emerging locality; social infrastructure is still developing.",
    },
    "loc-sirsi-road": {
        "walkability": 55, "schools": 58, "hospitals": 52, "connectivity": 74, "safety": 65,
        "notes": "Newer western corridor; suitable for long-term buyers who prioritise land appreciation.",
    },
}


def with_lifestyle(loc: dict) -> dict:
    """Attach lifestyle scores to a locality dict."""
    s = LIFESTYLE_SCORES.get(loc.get("id"))
    if not s:
        return loc
    overall = round((s["walkability"] + s["schools"] + s["hospitals"] + s["connectivity"] + s["safety"]) / 5)
    loc = {**loc, "lifestyle": {**s, "overall": overall}}
    return loc


def agent_tier(agent: dict) -> str:
    """Compute Bronze / Silver / Gold tier for an agent."""
    if not agent.get("verified"):
        return "Unverified"
    rera = bool(agent.get("rera_id"))
    reviews = int(agent.get("reviews") or 0)
    years = int(agent.get("years_exp") or 0)
    rating = float(agent.get("rating") or 0)
    # Gold: RERA + strong reviews + high rating
    if rera and reviews >= 80 and rating >= 4.6:
        return "Gold"
    # Silver: RERA or strong reviews
    if rera or reviews >= 60 or (years >= 10 and rating >= 4.5):
        return "Silver"
    return "Bronze"


def with_tier(agent: dict) -> dict:
    return {**agent, "tier": agent_tier(agent)}
