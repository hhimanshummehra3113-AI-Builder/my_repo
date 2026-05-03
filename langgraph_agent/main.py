"""
Main Entry Point - Run the LLM-Powered Banking CRM Agent with Ollama
"""
import sys
import os
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_agent.agent import run_agent


def check_services():
    """Check if required services are running"""
    services = {
        "Ollama LLM": ("http://localhost:11434", "ping"),
        "MCP Server": ("http://localhost:8000", "health")
    }
    
    all_ok = True
    for service_name, (url, endpoint) in services.items():
        try:
            full_url = f"{url}/{endpoint}"
            response = requests.get(full_url, timeout=2)
            if response.status_code in [200, 404]:
                print(f"✓ {service_name} is running ({url})")
            else:
                print(f"⚠ {service_name} returned status {response.status_code}")
                all_ok = False
        except requests.exceptions.ConnectionError:
            print(f"✗ {service_name} is NOT running ({url})")
            print(f"  Please start it with:")
            if service_name == "Ollama LLM":
                print(f"  $ ollama serve")
            else:
                print(f"  $ cd mcp_server && python main.py")
            all_ok = False
        except Exception as e:
            print(f"⚠ Error checking {service_name}: {str(e)}")
            all_ok = False
    
    return all_ok


def main():
    """
    Main entry point for the LLM-Powered Banking CRM Agent
    """
    print("\n" + "="*90)
    print("🤖 LLM-Powered Banking CRM Agent with Ollama + LangGraph")
    print("="*90 + "\n")
    
    # Check services
    print("Checking required services...\n")
    if not check_services():
        print("\n⚠️  Some services are not running. Please start them first.\n")
        return 1
    
    print("\n✓ All services ready!\n")
    
    # Mode selection
    print("="*90)
    print("Choose Agent Mode:")
    print("="*90)
    print("1. 📋 DETERMINISTIC (predefined workflow with all tools)")
    print("2. 💬 CONVERSATIONAL (interactive, intent-based, user query)")
    print("="*90 + "\n")
    
    mode = input("Select mode (1 or 2, default=2): ").strip() or "2"
    
    if mode == "1":
        return run_deterministic_agent()
    else:
        return run_conversational_agent_mode()


def run_deterministic_agent():
    """
    Run the original deterministic agent with predefined workflow
    """
    from langgraph_agent.agent import run_agent
    
    # Example queries the agent can handle
    queries = [
        "Identify high-value customers with 70+ conversion score for personal loan outreach",
        "Find premium segment customers with stable transaction history for auto loans",
        "Generate targeted outreach for customers with high loan eligibility"
    ]
    
    # Run agent with default query
    default_query = queries[0]
    
    print(f"\nStarting DETERMINISTIC agent with query: {default_query}\n")
    result = run_agent(user_query=default_query)
    
    if result:
        print("✅ Agent execution completed successfully!")
        print(f"\n📊 Results Summary:")
        print(f"  • Prospects identified: {len(result.high_value_prospects)}")
        print(f"  • Customers analyzed: {len(result.analyzed_customers)}")
        print(f"  • Recommendations generated: {len(result.recommendations)}")
        print(f"  • LLM reasoning steps: {len([t for t in result.thoughts if '🤖' in t or 'LLM' in t or '💭' in t or '📊' in t or '🎯' in t or '✍️' in t])}")
        print(f"  • Total iterations: {result.iterations_count}")
        print(f"  • Tools utilized: {', '.join(set(result.tools_called))}\n")
        
        if result.recommendations:
            print("📌 Sample Recommendations:")
            for rec in result.recommendations[:2]:
                print(f"\n  Customer {rec['customer_id']}:")
                print(f"    • Product: {rec['recommended_product']['product_name']}")
                print(f"    • Conversion: {rec['conversion_score']}/100")
                print(f"    • Message: {rec['outreach_message'][:80]}...\n")
        
        return 0
    else:
        print("❌ Agent execution failed")
        return 1


def run_conversational_agent_mode():
    """
    Run the conversational agent with user input
    """
    from langgraph_agent.conversational_agent import run_conversational_agent
    
    return run_conversational_agent() or 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

