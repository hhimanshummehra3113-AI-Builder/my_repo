"""
Conversational Banking CRM Agent with Intent Understanding
Accepts natural language user queries, analyzes intent, and dynamically routes to tools
"""
import sys
import os
import requests
from typing import Dict, List, Any
from dataclasses import dataclass, field

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_agent.llm_config import get_ollama_llm


# MCP Client to call tools via HTTP instead of direct import
class MCPClient:
    """Client to call MCP tools via HTTP API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Call a tool via MCP HTTP API"""
        try:
            response = requests.post(
                f"{self.base_url}/mcp/call",
                json={"tool": tool_name, "params": params},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"MCP call failed: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to call tool {tool_name}: {str(e)}")


@dataclass
class ConversationContext:
    """Context for a conversation turn"""
    user_query: str
    detected_intent: str = ""
    intent_confidence: float = 0.0
    required_tools: List[str] = field(default_factory=list)
    customer_segment: str = "high-value"  # "high-value" or "low-value"
    tool_results: Dict[str, Any] = field(default_factory=dict)
    llm_analysis: str = ""
    final_response: str = ""
    errors: List[str] = field(default_factory=list)


class ConversationalCRMAgent:
    """
    Conversational agent that understands user intent and dynamically uses tools
    """
    
    def __init__(self):
        # Initialize LLM - it will be checked on first use
        self.llm = get_ollama_llm(model="llama2", temperature=0.3)
        self.llm_available = self.llm is not None
        
        self.mcp_client = MCPClient(base_url="http://localhost:8000")
        self.conversation_history = []
    
    def analyze_intent(self, user_query: str) -> ConversationContext:
        """Use LLM to analyze user intent and select tools"""
        context = ConversationContext(user_query=user_query)
        
        # Check for low-value customer intent first
        query_lower = user_query.lower()
        if any(w in query_lower for w in ["low", "least", "poor", "worst", "bottom", "recovery", "at-risk", "struggling"]):
            context.customer_segment = "low-value"
        else:
            context.customer_segment = "high-value"
        
        if not self.llm_available:
            # Only use heuristic if LLM unavailable
            return self._heuristic_intent_detection(context)
        
        try:
            intent_prompt = f"""You are a banking CRM assistant. Analyze this query and determine which tools are needed.

Query: "{user_query}"

Available tools:
- identify_prospects: Find customers (high or low-value based on context)
- analyze_transactions: Analyze customer transaction patterns and stability
- conversion_score: Calculate customer conversion probability (0-100)
- recommended_products: Get eligible loan products for customer
- generate_message: Create personalized outreach messages

Return ONLY tool names as comma-separated list. Example: identify_prospects, recommended_products

Tools:"""
            
            response = self.llm.invoke(intent_prompt)
            tools_str = response.strip().strip("[]").strip('"').strip("'").lower()
            
            # Parse and validate tools
            if tools_str and tools_str != "none":
                tools = [t.strip() for t in tools_str.split(",")]
                valid_tools = ["identify_prospects", "analyze_transactions", "conversion_score", "recommended_products", "generate_message"]
                context.required_tools = [t for t in tools if t in valid_tools]
                
                # Always include identify_prospects as foundation
                if "identify_prospects" not in context.required_tools:
                    context.required_tools.insert(0, "identify_prospects")
                
                if context.required_tools:
                    return context
        except Exception as e:
            pass  # Fall back to heuristic on LLM error
        
        return self._heuristic_intent_detection(context)
    
    def _heuristic_intent_detection(self, context: ConversationContext) -> ConversationContext:
        """Fallback heuristic-based intent detection"""
        query_lower = context.user_query.lower()
        
        # Keywords for each tool
        tools_to_add = []
        
        # identify_prospects: "find", "identify", "list", "prospects", "customers", "who"
        if any(w in query_lower for w in ["find", "identify", "list", "who", "prospect", "customer", "discover", "search"]):
            tools_to_add.append("identify_prospects")
        
        # analyze_transactions: "analyze", "transaction", "pattern", "stability", "behavior"
        if any(w in query_lower for w in ["analyze", "examine", "transaction", "pattern", "stability", "behavior", "activity"]):
            tools_to_add.append("analyze_transactions")
        
        # conversion_score: "convert", "score", "likelihood", "probability", "eligible", "qualify"
        if any(w in query_lower for w in ["convert", "score", "likelihood", "probability", "eligible", "qualify", "potential"]):
            tools_to_add.append("conversion_score")
        
        # recommended_products: "recommend", "product", "loan", "offer", "eligible"
        if any(w in query_lower for w in ["recommend", "product", "loan", "offer", "eligible", "suitable", "suggest"]):
            tools_to_add.append("recommended_products")
        
        # generate_message: "generate", "message", "outreach", "personalize", "communicate", "send"
        if any(w in query_lower for w in ["generate", "message", "outreach", "personalize", "communicate", "send", "email", "contact"]):
            tools_to_add.append("generate_message")
        
        # Default to identify_prospects if nothing detected
        if not tools_to_add:
            tools_to_add = ["identify_prospects"]
        
        # Remove duplicates while preserving order
        seen = set()
        context.required_tools = [t for t in tools_to_add if not (t in seen or seen.add(t))]
        context.intent_confidence = 0.8
        
        return context
    
    def execute_tools(self, context: ConversationContext) -> ConversationContext:
        """Execute tools with optimized performance"""
        try:
            # Step 1: Call appropriate prospects tool based on segment
            tool_name = "identify_low_value_prospects" if context.customer_segment == "low-value" else "identify_high_value_prospects"
            result = self.mcp_client.call_tool(tool_name, {})
            
            # Extract prospects safely
            if isinstance(result, dict) and "result" in result:
                data = result["result"].get("data", {})
            elif isinstance(result, dict) and "data" in result:
                data = result["data"]
            else:
                data = {}
            
            # Get prospects based on segment
            if context.customer_segment == "low-value":
                prospects = data.get("bottom_prospects", [])
            else:
                prospects = data.get("top_prospects", [])
            
            context.tool_results["prospects"] = prospects
            if prospects:
                print(f"  ✓ Identified {len(prospects)} {context.customer_segment} prospects")
            
            # Step 2: Process top prospects efficiently (limit to 2 for speed)
            if prospects and len(context.required_tools) > 1:
                analyzed = []
                for prospect in prospects[:2]:  # Only top 2
                    customer_id = prospect.get("customer_id")
                    if not customer_id:
                        continue
                    
                    cust_data = {
                        "customer_id": customer_id,
                        "customer_name": prospect.get("customer_name") or prospect.get("name"),
                        "annual_income": prospect.get("annual_income"),
                        "conversion_score": prospect.get("conversion_score")
                    }
                    
                    # Get conversion score if needed
                    if "conversion_score" in context.required_tools:
                        try:
                            res = self.mcp_client.call_tool("calculate_conversion_score", {"customer_id": customer_id})
                            if isinstance(res, dict) and "result" in res:
                                score_data = res["result"].get("data", {})
                            else:
                                score_data = res
                            cust_data["score_detail"] = score_data
                        except:
                            pass
                    
                    # Get recommended products if needed
                    if "recommended_products" in context.required_tools:
                        try:
                            res = self.mcp_client.call_tool("get_recommended_products", {"customer_id": customer_id})
                            if isinstance(res, dict) and "result" in res:
                                prod_data = res["result"].get("data", {})
                                products = prod_data.get("eligible_products", []) if isinstance(prod_data, dict) else []
                            elif isinstance(res, list):
                                products = res
                            else:
                                products = []
                            cust_data["products"] = products
                            
                            # Generate message for top product
                            if "generate_message" in context.required_tools and products:
                                try:
                                    msg_res = self.mcp_client.call_tool(
                                        "generate_outreach_message",
                                        {"customer_id": customer_id, "product_id": products[0].get("product_id")}
                                    )
                                    if isinstance(msg_res, dict) and "result" in msg_res:
                                        msg = msg_res["result"].get("data", {})
                                    else:
                                        msg = msg_res
                                    cust_data["outreach_message"] = msg if isinstance(msg, str) else msg.get("message", "")
                                except:
                                    pass
                        except:
                            pass
                    
                    analyzed.append(cust_data)
                
                context.tool_results["analyzed_customers"] = analyzed
                if analyzed:
                    print(f"  ✓ Analyzed {len(analyzed)} customers with products & messages")
        
        except Exception as e:
            context.errors.append(f"Tool execution error: {str(e)}")
        
        return context
    
    def generate_response(self, context: ConversationContext) -> ConversationContext:
        """Generate natural language response using LLM with tool results"""
        if not self.llm_available:
            return self._generate_heuristic_response(context)
        
        # Format tool results for LLM context
        results_summary = self._summarize_tool_results(context)
        
        response_prompt = f"""You are a banking CRM expert. Based on the user's query and tool results, provide actionable insights and recommendations.

User Query: "{context.user_query}"

Tool Results:
{results_summary}

Provide specific, data-driven recommendations with customer details where available. Be concise but comprehensive."""
        
        try:
            response = self.llm.invoke(response_prompt)
            context.final_response = response.strip()
            return context
        except Exception as e:
            # Silent fallback to heuristic if LLM fails
            return self._generate_heuristic_response(context)
    
    def _generate_heuristic_response(self, context: ConversationContext) -> ConversationContext:
        """Generate response without LLM"""
        response_parts = []
        
        if context.tool_results.get("prospects"):
            prospects = context.tool_results["prospects"]
            response_parts.append(f"📊 Found {len(prospects)} high-value prospects:\n")
            for p in prospects[:3]:
                cid = p.get("customer_id")
                score = p.get("conversion_score", 0)
                likelihood = p.get("conversion_likelihood", "Unknown")
                response_parts.append(f"  • Customer {cid}: {score:.1f}/100 ({likelihood})")
        
        if context.tool_results.get("analyzed_customers"):
            customers = context.tool_results["analyzed_customers"]
            response_parts.append(f"\n💼 Analyzed {len(customers)} customers:")
            
            for c in customers[:3]:
                cid = c.get("customer_id")
                response_parts.append(f"\n  Customer {cid}:")
                
                if c.get("conversion_score"):
                    score_data = c["conversion_score"]
                    if isinstance(score_data, dict) and "data" in score_data:
                        score = score_data["data"].get("overall_conversion_score", 0)
                    else:
                        score = score_data.get("overall_conversion_score", 0)
                    response_parts.append(f"    Score: {score:.1f}/100")
                
                if c.get("recommended_products"):
                    prod = c["recommended_products"][0] if c["recommended_products"] else None
                    if prod:
                        response_parts.append(f"    Recommended: {prod.get('product_name', '?')}")
        
        context.final_response = "\n".join(response_parts) if response_parts else "No results found."
        return context
    
    def _summarize_tool_results(self, context: ConversationContext) -> str:
        """Summarize tool results for LLM"""
        summary = []
        
        if context.tool_results.get("prospects"):
            prospects = context.tool_results["prospects"]
            summary.append(f"Prospects: {len(prospects)} identified")
            for p in prospects[:3]:
                summary.append(f"  - Customer {p.get('customer_id')}: {p.get('conversion_score', 0):.1f}/100")
        
        if context.tool_results.get("analyzed_customers"):
            for c in context.tool_results["analyzed_customers"][:2]:
                summary.append(f"\nCustomer {c.get('customer_id')} ({c.get('customer_name', '?')}):")
                
                # Handle score safely
                if c.get("score_detail"):
                    score_data = c["score_detail"]
                    score = 0
                    if isinstance(score_data, dict):
                        if "data" in score_data:
                            score = score_data["data"].get("overall_conversion_score", 0)
                        else:
                            score = score_data.get("overall_conversion_score", 0)
                    elif isinstance(score_data, (int, float)):
                        score = float(score_data)
                    
                    summary.append(f"  Score: {score:.1f}/100")
                
                # Handle products
                if c.get("products"):
                    prod = c["products"][0] if c["products"] else None
                    if prod:
                        summary.append(f"  Recommended: {prod.get('product_name')} ({prod.get('interest_rate', 'N/A')}%)")
                
                # Handle message
                if c.get("outreach_message"):
                    msg = c["outreach_message"]
                    if isinstance(msg, dict):
                        msg = msg.get("message", str(msg)[:100])
                    summary.append(f"  Message: {str(msg)[:100]}...")
        
        return "\n".join(summary) if summary else "No results"
    
    def process_query(self, user_query: str) -> str:
        """Main entry point to process a user query"""
        print(f"\n{'='*80}")
        print(f"🤖 Processing: {user_query}")
        print(f"{'='*80}\n")
        
        # Analyze intent
        print("📍 Step 1: Analyzing intent...")
        context = self.analyze_intent(user_query)
        mode = "🧠 LLM-Based Agentic AI" if self.llm_available else "⚙️ Heuristic Fallback"
        print(f"  ✓ Mode: {mode}")
        print(f"  ✓ Tools: {', '.join(context.required_tools)}")
        
        # Execute tools
        print(f"\n📍 Step 2: Executing tools...")
        context = self.execute_tools(context)
        for error in context.errors[:3]:
            print(f"  ⚠ {error}")
        
        # Generate response
        print(f"\n📍 Step 3: Generating response...")
        context = self.generate_response(context)
        
        self.conversation_history.append(context)
        
        print(f"\n{'='*80}")
        print(f"📌 Response:\n")
        print(context.final_response)
        print(f"\n{'='*80}\n")
        
        return context.final_response


def run_conversational_agent():
    """Run the conversational agent interactively"""
    
    print("\n" + "="*80)
    print("🤖 Conversational Banking CRM Agent")
    print("="*80 + "\n")
    
    agent = ConversationalCRMAgent()
    
    print("Enter queries (type 'quit' to exit):\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                print("\n👋 Thank you!")
                break
            if user_input:
                agent.process_query(user_input)
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Agent stopped")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    run_conversational_agent()
