import requests
import json

base_url = "http://localhost:8000/mcp/call"
tools = [
    {"tool": "get_customer_profile", "params": {"customer_id": 1}},
    {"tool": "analyze_transactions", "params": {"customer_id": 1, "months": 6}},
    {"tool": "calculate_conversion_score", "params": {"customer_id": 1}},
    {"tool": "get_recommended_products", "params": {"customer_id": 1}},
    {"tool": "generate_outreach_message", "params": {"customer_id": 1, "product_id": 1}},
    {"tool": "identify_high_value_prospects", "params": {}},
]

for tool_def in tools:
    try:
        r = requests.post(base_url, json=tool_def, timeout=5)
        result = r.json()
        success = result.get("success", False) and "error" not in result.get("result", {})
        status = "✓" if success else "✗"
        print(f"{status} {tool_def['tool']}: ", end="")
        if success:
            print("SUCCESS")
        else:
            print(f"FAILED - {result.get('result', {}).get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ {tool_def['tool']}: ERROR - {str(e)}")
