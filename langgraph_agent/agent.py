"""
LLM-Powered LangGraph Agent - With Ollama integration for ReAct reasoning
"""
from langgraph.graph import StateGraph, END
from .state import AgentState
from .llm_nodes import (
    plan_node,
    identify_prospects_node,
    analyze_customers_node,
    generate_recommendations_node,
    finalize_node,
)


def create_crm_agent():
    """
    Create and compile the LLM-Powered Banking CRM Agent with LangGraph
    
    Agent Flow with LLM Reasoning:
    1. Plan - LLM decides initial strategy
    2. Identify high-value prospects (conversion score 70+)
    3. Analyze customer profiles with LLM interpretation
    4. Generate personalized product recommendations with LLM optimization
    5. Create targeted outreach messages enhanced by LLM
    6. Finalize with LLM-generated executive summary
    """
    
    # Create state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes - with LLM integration
    workflow.add_node("plan", plan_node)
    workflow.add_node("identify_prospects", identify_prospects_node)
    workflow.add_node("analyze_customers", analyze_customers_node)
    workflow.add_node("generate_recommendations", generate_recommendations_node)
    workflow.add_node("finalize", finalize_node)
    
    # Add edges with LLM-guided flow
    workflow.add_edge("plan", "identify_prospects")
    workflow.add_edge("identify_prospects", "analyze_customers")
    workflow.add_edge("analyze_customers", "generate_recommendations")
    workflow.add_edge("generate_recommendations", "finalize")
    
    # End node
    workflow.add_edge("finalize", END)
    
    # Set entry point
    workflow.set_entry_point("plan")
    
    # Compile the graph
    agent = workflow.compile()
    
    return agent


def run_agent(user_query: str = "Identify high-value customers with 70+ conversion score for personal loan outreach"):
    """
    Run the LLM-Powered Banking CRM Agent with a given query
    
    Args:
        user_query: The task for the agent to perform
    
    Returns:
        Final agent state with results
    """
    # Create agent
    agent = create_crm_agent()
    
    # Initialize state
    initial_state = AgentState(
        user_query=user_query,
        customer_ids=[],
        high_value_prospects=[],
        analyzed_customers=[],
        tools_called=[],
        tool_results={},
        thoughts=[],
        current_action="",
        recommendations=[],
        summary="",
        error=None,
        next_node="plan",
        max_iterations=10,
        iterations_count=0
    )
    
    # Execute agent
    print(f"\n{'='*90}")
    print(f"🤖 LLM-Powered Banking CRM Agent Starting (Ollama + LangGraph)")
    print(f"{'='*90}")
    print(f"Task: {user_query}\n")
    
    try:
        # Run the agent
        final_state_dict = agent.invoke(initial_state)
        
        # Convert dict back to AgentState if needed
        if isinstance(final_state_dict, dict):
            final_state = AgentState(**final_state_dict)
        else:
            final_state = final_state_dict
        
        # Print execution log with LLM thoughts
        print(f"\n{'='*90}")
        print(f"📊 Agent Execution Log (with LLM Reasoning)")
        print(f"{'='*90}")
        for thought in final_state.thoughts:
            print(thought)
        
        # Print summary
        print(f"\n{'='*90}")
        print(f"📋 Executive Summary")
        print(f"{'='*90}")
        print(final_state.summary)
        
        # Print recommendations
        if final_state.recommendations:
            print(f"\n{'='*90}")
            print(f"💼 LLM-Optimized Recommendations")
            print(f"{'='*90}")
            for i, rec in enumerate(final_state.recommendations, 1):
                print(f"\n{i}. Customer ID: {rec['customer_id']}")
                print(f"   Conversion Score: {rec['conversion_score']}/100 ({rec['conversion_likelihood']})")
                print(f"   Recommended Product: {rec['recommended_product']['product_name']}")
                print(f"   Personalization Tier: {rec['personalization']}")
                print(f"   LLM-Enhanced Message: {rec['outreach_message'][:120]}...")
        
        if final_state.error:
            print(f"\n⚠️ Error: {final_state.error}")
        
        print(f"\n{'='*90}")
        print(f"✅ Agent execution completed!")
        print(f"   Iterations: {final_state.iterations_count}")
        print(f"   Tools called: {len(set(final_state.tools_called))}")
        print(f"{'='*90}\n")
        
        return final_state
        
    except Exception as e:
        print(f"❌ Agent execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
