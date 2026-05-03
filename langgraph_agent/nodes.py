"""
Agent Nodes - Processing logic for each step of the agent
"""
import requests
import json
from typing import Dict, Any
from datetime import datetime
from .state import AgentState


class MCSPClient:
    """Client to communicate with MCP Server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            response = requests.post(
                f"{self.base_url}/mcp/call",
                json={"tool": tool_name, "params": params},
                timeout=10
            )
            result = response.json()
            return result.get("result", {})
        except Exception as e:
            return {"error": str(e), "success": False}


# Global MCP client
mcp_client = MCSPClient()


def identify_prospects_node(state: AgentState) -> AgentState:
    """
    Node: Identify high-value prospects
    Calls MCP server to get top customers for loan outreach
    """
    state.current_action = "Identifying high-value prospects for personal loan offers"
    state.thoughts.append(f"[{datetime.now().isoformat()}] Starting high-value prospect identification")
    state.iterations_count += 1
    
    try:
        # Call the identify_high_value_prospects tool
        result = mcp_client.call_tool("identify_high_value_prospects", {})
        
        if result.get("success"):
            prospects = result.get("data", {}).get("top_prospects", [])
            state.high_value_prospects = prospects
            state.customer_ids = [p["customer_id"] for p in prospects]
            state.tool_results["identify_prospects"] = result
            state.tools_called.append("identify_high_value_prospects")
            
            state.thoughts.append(
                f"✓ Identified {len(prospects)} high-value prospects. "
                f"Immediate priority: {result.get('data', {}).get('summary', {}).get('immediate_priority', 0)}"
            )
            state.next_node = "analyze_customers"
        else:
            state.error = result.get("error", "Failed to identify prospects")
            state.thoughts.append(f"✗ Error: {state.error}")
            state.next_node = "end"
    except Exception as e:
        state.error = str(e)
        state.thoughts.append(f"✗ Exception: {state.error}")
        state.next_node = "end"
    
    return state


def analyze_customers_node(state: AgentState) -> AgentState:
    """
    Node: Analyze each prospect in detail
    Gets conversion scores, transaction analysis, and product recommendations
    """
    state.current_action = "Analyzing customer profiles and conversion potential"
    state.thoughts.append(f"[{datetime.now().isoformat()}] Analyzing {len(state.customer_ids)} customers")
    state.iterations_count += 1
    
    analyzed_count = 0
    for customer_id in state.customer_ids[:5]:  # Analyze top 5 to keep execution quick
        try:
            # Get conversion score
            score_result = mcp_client.call_tool("calculate_conversion_score", {"customer_id": customer_id})
            
            # Get transaction analysis
            trans_result = mcp_client.call_tool("analyze_transactions", {
                "customer_id": customer_id,
                "months": 6
            })
            
            if score_result.get("success") and trans_result.get("success"):
                customer_analysis = {
                    "customer_id": customer_id,
                    "conversion_score": score_result.get("data", {}).get("overall_conversion_score", 0),
                    "conversion_likelihood": score_result.get("data", {}).get("conversion_likelihood", "Unknown"),
                    "stability_score": trans_result.get("data", {}).get("stability_score", 0),
                    "transaction_data": trans_result.get("data", {})
                }
                state.analyzed_customers.append(customer_analysis)
                analyzed_count += 1
                state.tools_called.extend(["calculate_conversion_score", "analyze_transactions"])
        except Exception as e:
            state.thoughts.append(f"⚠ Error analyzing customer {customer_id}: {str(e)}")
    
    state.thoughts.append(f"✓ Successfully analyzed {analyzed_count} customers")
    state.next_node = "generate_recommendations"
    
    return state


def generate_recommendations_node(state: AgentState) -> AgentState:
    """
    Node: Generate product recommendations and outreach messages
    """
    state.current_action = "Generating personalized product recommendations and outreach messages"
    state.thoughts.append(f"[{datetime.now().isoformat()}] Generating recommendations")
    state.iterations_count += 1
    
    recommendations_generated = 0
    for customer_data in state.analyzed_customers[:3]:  # Top 3
        customer_id = customer_data["customer_id"]
        
        try:
            # Get recommended products
            products_result = mcp_client.call_tool("get_recommended_products", {"customer_id": customer_id})
            
            if products_result.get("success"):
                products = products_result.get("data", {}).get("recommendations", [])
                
                if products:
                    # Generate outreach message for top product
                    product_id = products[0]["product_id"]
                    message_result = mcp_client.call_tool("generate_outreach_message", {
                        "customer_id": customer_id,
                        "product_id": product_id
                    })
                    
                    if message_result.get("success"):
                        recommendation = {
                            "customer_id": customer_id,
                            "conversion_score": customer_data["conversion_score"],
                            "conversion_likelihood": customer_data["conversion_likelihood"],
                            "recommended_product": products[0],
                            "outreach_message": message_result.get("data", {}).get("message_content", ""),
                            "personalization": message_result.get("data", {}).get("personalization_tier", ""),
                            "timestamp": datetime.now().isoformat()
                        }
                        state.recommendations.append(recommendation)
                        recommendations_generated += 1
                        state.tools_called.extend(["get_recommended_products", "generate_outreach_message"])
        except Exception as e:
            state.thoughts.append(f"⚠ Error generating recommendation for customer {customer_id}: {str(e)}")
    
    state.thoughts.append(f"✓ Generated {recommendations_generated} recommendations")
    state.next_node = "finalize"
    
    return state


def finalize_node(state: AgentState) -> AgentState:
    """
    Node: Finalize and summarize agent execution
    """
    state.current_action = "Finalizing recommendations"
    state.thoughts.append(f"[{datetime.now().isoformat()}] Finalizing execution")
    state.iterations_count += 1
    
    # Generate summary
    immediate_priority = len([p for p in state.high_value_prospects if p.get("priority") == "IMMEDIATE"])
    high_priority = len([p for p in state.high_value_prospects if p.get("priority") == "HIGH"])
    
    summary_parts = [
        f"✓ Banking CRM Agent Execution Complete",
        f"  • Identified {len(state.high_value_prospects)} high-value prospects",
        f"  • Analyzed {len(state.analyzed_customers)} customers in detail",
        f"  • Generated {len(state.recommendations)} personalized recommendations",
        f"  • Tools called: {', '.join(set(state.tools_called))}",
        f"  • Immediate priority candidates: {immediate_priority}",
        f"  • High priority candidates: {high_priority}",
        f"  • Iterations: {state.iterations_count}/{state.max_iterations}"
    ]
    
    state.summary = "\n".join(summary_parts)
    state.next_node = "end"
    
    return state


def router_node(state: AgentState) -> str:
    """
    Router: Decide which node to execute next
    """
    if state.error:
        return "finalize"
    
    if state.iterations_count >= state.max_iterations:
        return "finalize"
    
    return state.next_node


# Node mapping
NODES = {
    "identify_prospects": identify_prospects_node,
    "analyze_customers": analyze_customers_node,
    "generate_recommendations": generate_recommendations_node,
    "finalize": finalize_node,
}
