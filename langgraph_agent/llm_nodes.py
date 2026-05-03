"""
LLM-Enhanced Agent Nodes - Using Ollama for ReAct-style reasoning
"""
import requests
import json
from datetime import datetime
from typing import Dict, Any
from .state import AgentState
from .llm_config import get_ollama_llm


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


# Global MCP client and LLM
mcp_client = MCSPClient()
llm = get_ollama_llm(model="llama2", temperature=0.3)


TOOL_DESCRIPTIONS = {
    "identify_high_value_prospects": "Identifies top 10 high-value customers with high conversion probability for loan products. Returns customer IDs, names, conversion scores.",
    "get_customer_profile": "Gets detailed profile of a specific customer including financial info, account status, and loan history.",
    "analyze_transactions": "Analyzes customer transaction patterns for 6 months including frequency, stability score, and spending categories.",
    "calculate_conversion_score": "Calculates multi-factor conversion score (0-100) for a customer based on credit, income, transaction stability, and tenure.",
    "get_recommended_products": "Gets list of loan products a customer is eligible for with estimated interest rates and EMI.",
    "generate_outreach_message": "Generates personalized SMS/WhatsApp message for a specific customer and product based on their profile."
}


def plan_node(state: AgentState) -> AgentState:
    """
    LLM Planning Node - Agent decides what to do first
    Uses LLM to reason about the task
    """
    state.current_action = "Planning agent strategy"
    state.iterations_count += 1
    
    if not llm:
        state.error = "Ollama LLM not available"
        state.next_node = "end"
        return state
    
    prompt = f"""You are a Banking CRM agent. Your task is to: {state.user_query}

Available tools:
{json.dumps(TOOL_DESCRIPTIONS, indent=2)}

Analyze this task and decide what to do first. Should we:
1. identify_high_value_prospects - Find top customers for outreach
2. get_customer_profile - Get details of specific customers
3. analyze_transactions - Analyze customer behavior

Respond with ONLY the tool name, nothing else."""
    
    try:
        response = llm.invoke(prompt)
        thought = f"[{datetime.now().isoformat()}] Agent Planning: {response.strip()}"
        state.thoughts.append(thought)
        
        if "identify_high_value_prospects" in response.lower():
            state.next_node = "identify_prospects"
        else:
            state.next_node = "identify_prospects"  # Default
            
    except Exception as e:
        state.thoughts.append(f"⚠ Planning error: {str(e)}")
        state.next_node = "identify_prospects"
    
    return state


def identify_prospects_node(state: AgentState) -> AgentState:
    """
    Identify Prospects Node - With LLM analysis
    """
    state.current_action = "Identifying high-value prospects"
    state.iterations_count += 1
    state.thoughts.append(f"[{datetime.now().isoformat()}] Calling identify_high_value_prospects")
    
    try:
        # Call tool
        result = mcp_client.call_tool("identify_high_value_prospects", {})
        
        if result.get("success"):
            prospects = result.get("data", {}).get("top_prospects", [])
            state.high_value_prospects = prospects
            state.customer_ids = [p["customer_id"] for p in prospects]
            state.tool_results["identify_prospects"] = result
            state.tools_called.append("identify_high_value_prospects")
            
            summary = result.get("data", {}).get("summary", {})
            state.thoughts.append(
                f"✓ Identified {len(prospects)} high-value prospects. "
                f"Immediate: {summary.get('immediate_priority', 0)}, "
                f"High: {summary.get('high_priority', 0)}, "
                f"Medium: {summary.get('medium_priority', 0)}"
            )
            
            # Use LLM to interpret results
            if llm:
                prompt = f"""Analyze these {len(prospects)} identified prospects and provide insights on what we should do next:
                
Prospects:
{json.dumps(prospects[:3], indent=2)}

Should we analyze their transaction patterns, get product recommendations, or something else?
Respond concisely in 1-2 sentences."""
                
                try:
                    interpretation = llm.invoke(prompt)
                    state.thoughts.append(f"📊 LLM Analysis: {interpretation.strip()}")
                except Exception as e:
                    state.thoughts.append(f"⚠ LLM analysis failed: {str(e)}")
            
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
    Analyze Customers Node - LLM-guided analysis
    """
    state.current_action = "Analyzing customer profiles and conversion potential"
    state.iterations_count += 1
    state.thoughts.append(f"[{datetime.now().isoformat()}] Analyzing {len(state.customer_ids)} customers")
    
    analyzed_count = 0
    for customer_id in state.customer_ids[:5]:  # Top 5
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
                
                # LLM assessment of this customer
                if llm and analyzed_count == 1:  # Analyze first customer with LLM detail
                    prompt = f"""Based on this customer's profile, what's your assessment:
                    
Conversion Score: {customer_analysis['conversion_score']}/100
Likelihood: {customer_analysis['conversion_likelihood']}
Stability: {customer_analysis['stability_score']}/100

Should we proceed with product recommendations?"""
                    
                    try:
                        assessment = llm.invoke(prompt)
                        state.thoughts.append(f"💭 LLM Assessment: {assessment.strip()}")
                    except:
                        pass
                        
        except Exception as e:
            state.thoughts.append(f"⚠ Error analyzing customer {customer_id}: {str(e)}")
    
    state.thoughts.append(f"✓ Successfully analyzed {analyzed_count} customers")
    state.next_node = "generate_recommendations"
    
    return state


def generate_recommendations_node(state: AgentState) -> AgentState:
    """
    Generate Recommendations Node - LLM-optimized recommendations
    """
    state.current_action = "Generating personalized product recommendations"
    state.iterations_count += 1
    state.thoughts.append(f"[{datetime.now().isoformat()}] Generating recommendations")
    
    recommendations_generated = 0
    for customer_data in state.analyzed_customers[:3]:  # Top 3
        customer_id = customer_data["customer_id"]
        
        try:
            # Get recommended products
            products_result = mcp_client.call_tool("get_recommended_products", {"customer_id": customer_id})
            
            if products_result.get("success"):
                products = products_result.get("data", {}).get("recommendations", [])
                
                if products:
                    # Use LLM to select best product
                    if llm:
                        prompt = f"""Given these {len(products)} product options for a customer with {customer_data['conversion_score']}/100 conversion score:

{json.dumps([{'name': p['product_name'], 'rate': p['estimated_rate'], 'emi': p['monthly_emi_estimate']} for p in products], indent=2)}

Which product is best for this customer and why? Respond in 1 sentence."""
                        
                        try:
                            product_choice = llm.invoke(prompt)
                            state.thoughts.append(f"🎯 Product Selection: {product_choice.strip()}")
                        except Exception as e:
                            state.thoughts.append(f"⚠ LLM selection failed, using top product")
                    
                    # Generate outreach message for top product
                    product_id = products[0]["product_id"]
                    message_result = mcp_client.call_tool("generate_outreach_message", {
                        "customer_id": customer_id,
                        "product_id": product_id
                    })
                    
                    if message_result.get("success"):
                        # Use LLM to enhance the message
                        base_message = message_result.get("data", {}).get("message_content", "")
                        
                        if llm:
                            prompt = f"""Improve this outreach message to make it more compelling:

Original: {base_message[:150]}...

Make it more personalized and action-oriented. Keep it under 160 characters for SMS."""
                            
                            try:
                                enhanced_message = llm.invoke(prompt)
                                final_message = enhanced_message.strip()
                                state.thoughts.append(f"✍️ Message Enhanced by LLM")
                            except:
                                final_message = base_message
                        else:
                            final_message = base_message
                        
                        recommendation = {
                            "customer_id": customer_id,
                            "conversion_score": customer_data["conversion_score"],
                            "conversion_likelihood": customer_data["conversion_likelihood"],
                            "recommended_product": products[0],
                            "outreach_message": final_message,
                            "personalization": message_result.get("data", {}).get("personalization_tier", ""),
                            "timestamp": datetime.now().isoformat()
                        }
                        state.recommendations.append(recommendation)
                        recommendations_generated += 1
                        state.tools_called.extend(["get_recommended_products", "generate_outreach_message"])
                        
        except Exception as e:
            state.thoughts.append(f"⚠ Error generating recommendation for customer {customer_id}: {str(e)}")
    
    state.thoughts.append(f"✓ Generated {recommendations_generated} LLM-optimized recommendations")
    state.next_node = "finalize"
    
    return state


def finalize_node(state: AgentState) -> AgentState:
    """
    Finalize Node - LLM-generated summary
    """
    state.current_action = "Finalizing recommendations"
    state.iterations_count += 1
    state.thoughts.append(f"[{datetime.now().isoformat()}] Finalizing execution")
    
    # Generate executive summary with LLM
    if llm:
        prompt = f"""Generate a brief executive summary of this Banking CRM campaign:
        
- Identified: {len(state.high_value_prospects)} high-value prospects
- Analyzed: {len(state.analyzed_customers)} customers in depth
- Recommendations: {len(state.recommendations)} personalized offers
- Tools Used: {len(set(state.tools_called))} MCP tools

Keep it to 2-3 sentences."""
        
        try:
            llm_summary = llm.invoke(prompt)
            state.summary = f"LLM Executive Summary:\n{llm_summary.strip()}"
        except Exception as e:
            state.summary = "Executive summary generation failed"
    else:
        immediate_priority = len([p for p in state.high_value_prospects if p.get("priority") == "IMMEDIATE"])
        high_priority = len([p for p in state.high_value_prospects if p.get("priority") == "HIGH"])
        
        summary_parts = [
            f"✓ Banking CRM Agent Execution Complete",
            f"  • Identified {len(state.high_value_prospects)} high-value prospects",
            f"  • Analyzed {len(state.analyzed_customers)} customers in detail",
            f"  • Generated {len(state.recommendations)} personalized recommendations",
            f"  • Immediate priority candidates: {immediate_priority}",
            f"  • High priority candidates: {high_priority}",
        ]
        state.summary = "\n".join(summary_parts)
    
    state.next_node = "end"
    
    return state


# Node mapping
NODES = {
    "plan": plan_node,
    "identify_prospects": identify_prospects_node,
    "analyze_customers": analyze_customers_node,
    "generate_recommendations": generate_recommendations_node,
    "finalize": finalize_node,
}
