#!/usr/bin/env python3
"""
Demo: Conversational Banking CRM Agent with Example Queries
Tests the conversational agent with predefined queries without requiring user input
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_agent.conversational_agent import ConversationalCRMAgent


def demo_conversational_agent():
    """
    Run demo queries through the conversational agent
    """
    import requests
    
    print("\n" + "="*90)
    print("🤖 Conversational Banking CRM Agent - DEMO MODE")
    print("="*90 + "\n")
    
    # Check services
    print("Checking required services...\n")
    try:
        mcp_response = requests.get("http://localhost:8000/health", timeout=2)
        print(f"✓ MCP Server is running (http://localhost:8000)")
    except:
        print(f"✗ MCP Server is NOT running")
        print(f"  Please start: cd mcp_server && python main.py")
        return 1
    
    try:
        ollama_response = requests.get("http://localhost:11434/api/tags", timeout=2)
        print(f"✓ Ollama LLM is running (http://localhost:11434)")
    except:
        print(f"⚠ Ollama LLM is NOT running or llama2 model not ready")
        print(f"  Please start: ollama serve (in another terminal)")
    
    print("\n✓ Ready to process queries!\n")
    
    # Initialize agent
    print("Initializing Conversational Agent...")
    agent = ConversationalCRMAgent()
    print("✓ Agent initialized\n")
    
    # Demo queries
    demo_queries = [
        "Find high-value customers likely to convert for a personal loan this month and generate personalized messages",
        "Identify customers with stable transaction patterns for auto loan eligibility",
        "Show me top conversion prospects with recommended products"
    ]
    
    print("="*90)
    print("📋 DEMO QUERIES")
    print("="*90 + "\n")
    
    for i, query in enumerate(demo_queries, 1):
        print(f"Query {i}: {query}\n")
        
        try:
            response = agent.process_query(query)
            print("✓ Query processed successfully\n")
            
            # Pause between queries
            if i < len(demo_queries):
                input("Press Enter to continue to next query...")
                print()
        
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}\n")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*90)
    print("✅ Demo completed!")
    print("="*90)
    print("\n💡 Try running the interactive mode:")
    print("   python langgraph_agent/main.py")
    print("   Then select option 2 (CONVERSATIONAL)\n")
    
    return 0


if __name__ == "__main__":
    exit_code = demo_conversational_agent()
    sys.exit(exit_code)
