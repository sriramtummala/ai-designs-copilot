GET_BRAND_INFO_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_brand_info",
        "description": "Get specific information about a brand, such as its tone of voice, key messaging, or target audience.",
        "parameters": {
            "type": "object",
            "properties": {
                "brand_name": {
                    "type": "string",
                    "description": "The name of the brand (e.g., brand_a, brand_b)."
                },
                "info_type": {
                    "type": "string",
                    "enum": ["tone_of_voice", "key_messaging", "target_audience", "all"],
                    "description": "The type of information to retrieve about the brand."
                }
            },
            "required": ["brand_name", "info_type"]
        }
    }
}
 
# List of all available tools
AVAILABLE_TOOLS = [
    GET_BRAND_INFO_TOOL_SCHEMA,
    # Add other tool schemas here as you create them
]
