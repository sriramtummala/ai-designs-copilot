from typing import Dict, Any

BRAND_DATA = {
    "brand_a": {
        "tone_of_voice": "Friendly, innovative, and empowering.",
        "key_messaging": "Simplifying complex tasks, empowering creativity.",
        "target_audience": "Creative professionals, small businesses.",
    },
    "brand_b": {
        "tone_of_voice": "Authoritative, technical, and precise.",
        "key_messaging": "Cutting-edge technology, robust solutions, developer-centric.",
        "target_audience": "Software developers, enterprise clients.",
    },
}


def get_brand_info(brand_name: str, info_type: str) -> Dict[str, Any]:
    """Return brand metadata. info_type: 'tone_of_voice' | 'key_messaging' | 'target_audience' | 'all'."""
    brand = BRAND_DATA.get(brand_name.lower())
    if not brand:
        return {"error": f"Brand '{brand_name}' not found.", "brand_name": brand_name}

    if info_type == "all":
        return {"brand_name": brand_name, "info": brand}

    value = brand.get(info_type.lower())
    if value is None:
        return {
            "error": f"Unknown info_type '{info_type}' for '{brand_name}'.",
            "available": list(brand.keys()),
        }

    return {"brand_name": brand_name, info_type: value}


TOOL_FUNCTIONS: Dict[str, Any] = {
    "get_brand_info": get_brand_info,
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_brand_info",
            "description": "Retrieves tone of voice, key messaging, or target audience for a brand.",
            "parameters": {
                "type": "object",
                "properties": {
                    "brand_name": {
                        "type": "string",
                        "description": "The brand identifier, e.g. 'brand_a' or 'brand_b'.",
                    },
                    "info_type": {
                        "type": "string",
                        "enum": ["tone_of_voice", "key_messaging", "target_audience", "all"],
                        "description": "Which piece of brand information to retrieve.",
                    },
                },
                "required": ["brand_name", "info_type"],
            },
        },
    },
]
