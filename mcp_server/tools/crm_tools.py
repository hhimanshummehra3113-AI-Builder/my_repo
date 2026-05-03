"""
Banking CRM Tool Handlers for MCP Server
Implements all tools for customer analysis, scoring, and outreach
"""
from typing import Dict, Any, List
from db.customer_repo import customer_repo
from db.transaction_repo import transaction_repo
from db.product_repo import product_repo
from db.loan_repo import loan_repo
import json
from datetime import datetime


class CRMTools:
    """All CRM-related tools for the MCP server"""
    
    @staticmethod
    def get_customer_profile(customer_id: int) -> Dict[str, Any]:
        """
        Tool: Fetch complete customer profile
        
        Input: customer_id (int)
        Output: Complete customer details with financials and status
        """
        customer = customer_repo.get_customer_by_id(customer_id)
        
        if not customer:
            return {
                "success": False,
                "error": f"Customer {customer_id} not found",
                "data": None
            }
        
        # Get active loans
        active_loans = loan_repo.get_customer_active_loans(customer_id)
        
        # Check default history
        has_default = loan_repo.has_default_history(customer_id)
        
        return {
            "success": True,
            "data": {
                "customer_id": customer['id'],
                "name": f"{customer['first_name']} {customer['last_name']}",
                "email": customer['email'],
                "phone": customer['phone'],
                "contact": {
                    "email": customer['email'],
                    "phone": customer['phone']
                },
                "financial_profile": {
                    "annual_income": float(customer['annual_income']) if customer['annual_income'] else 0,
                    "credit_score": customer['credit_score'],
                    "employment_status": customer['employment_status'],
                    "employment_type": customer['employment_type']
                },
                "account_info": {
                    "tenure_months": customer['account_tenure_months'],
                    "segment": customer.get('segment_name', 'Unknown'),
                    "status": customer['account_status'],
                    "last_transaction_date": customer['last_transaction_date'].isoformat() if customer['last_transaction_date'] else None,
                    "total_deposits": float(customer['total_deposits']) if customer['total_deposits'] else 0,
                    "total_withdrawals": float(customer['total_withdrawals']) if customer['total_withdrawals'] else 0
                },
                "loan_info": {
                    "active_loans": len(active_loans),
                    "active_loans_details": active_loans,
                    "default_history": has_default
                }
            }
        }
    
    @staticmethod
    def analyze_transactions(customer_id: int, months: int = 6) -> Dict[str, Any]:
        """
        Tool: Analyze customer transaction patterns
        
        Input: customer_id (int), months (int, default=6)
        Output: Transaction analysis with patterns and trends
        """
        customer = customer_repo.get_customer_by_id(customer_id)
        if not customer:
            return {
                "success": False,
                "error": f"Customer {customer_id} not found",
                "data": None
            }
        
        # Get transaction patterns
        patterns = transaction_repo.analyze_transaction_patterns(customer_id, months)
        
        # Get category breakdown
        category_breakdown = transaction_repo.get_category_breakdown(customer_id, months)
        
        # Get monthly trend
        monthly_trend = transaction_repo.get_monthly_transaction_trend(customer_id, months)
        
        # Calculate stability score
        stability = transaction_repo.calculate_stability_score(customer_id, months)
        
        if not patterns:
            return {
                "success": False,
                "error": f"No transaction data for customer {customer_id}",
                "data": None
            }
        
        return {
            "success": True,
            "data": {
                "customer_id": customer_id,
                "analysis_period_months": months,
                "summary": {
                    "total_transactions": patterns.get('total_transactions', 0),
                    "active_days": patterns.get('transaction_days', 0),
                    "total_credits": float(patterns.get('total_credits', 0)),
                    "total_debits": float(patterns.get('total_debits', 0)),
                    "net_flow": float((patterns.get('total_credits', 0) or 0) - (patterns.get('total_debits', 0) or 0))
                },
                "average_metrics": {
                    "avg_transaction_amount": float(patterns.get('avg_transaction_amount', 0) or 0),
                    "max_transaction": float(patterns.get('max_transaction_amount', 0) or 0),
                    "min_transaction": float(patterns.get('min_transaction_amount', 0) or 0),
                    "std_deviation": float(patterns.get('stddev_amount', 0) or 0)
                },
                "activity_metrics": {
                    "active_months": patterns.get('active_months', 0),
                    "last_transaction": patterns.get('last_transaction_date').isoformat() if patterns.get('last_transaction_date') else None,
                    "active_months_ratio": f"{round((patterns.get('active_months', 0) / months) * 100, 1)}%"
                },
                "stability_score": stability,
                "category_breakdown": category_breakdown,
                "monthly_trend": monthly_trend
            }
        }
    
    @staticmethod
    def calculate_conversion_score(customer_id: int) -> Dict[str, Any]:
        """
        Tool: Calculate likelihood of loan conversion for customer
        
        Input: customer_id (int)
        Output: Conversion score (0-100) with breakdown
        """
        customer = customer_repo.get_customer_by_id(customer_id)
        if not customer:
            return {
                "success": False,
                "error": f"Customer {customer_id} not found",
                "data": None
            }
        
        # Get transaction analysis
        trans_data = transaction_repo.analyze_transaction_patterns(customer_id, 6)
        stability = transaction_repo.calculate_stability_score(customer_id, 6)
        
        # Get loan history
        active_loans = loan_repo.get_customer_active_loans(customer_id)
        has_default = loan_repo.has_default_history(customer_id)
        
        # Calculate scores for each factor
        
        # 1. Credit Score Component (30%)
        credit_score = customer['credit_score'] or 0
        credit_component = min((credit_score / 850) * 100, 100)
        
        # 2. Income Component (25%)
        annual_income = float(customer['annual_income']) or 0
        income_component = min((annual_income / 1000000) * 100, 100)
        
        # 3. Transaction Stability Component (25%)
        stability_score = stability.get('stability_score', 0)
        stability_component = min(stability_score, 100)
        
        # 4. Account Tenure Component (10%)
        tenure_months = customer['account_tenure_months'] or 0
        tenure_component = min((tenure_months / 60) * 100, 100)  # 5 years = 100%
        
        # 5. Loan Behavior Component (10%)
        emi_payment_score = 100 if len(active_loans) > 0 else 50  # Has existing loans = good
        default_penalty = 0 if has_default else 100  # Default history = 0 points
        loan_component = (emi_payment_score * 0.5 + default_penalty * 0.5)
        
        # Calculate weighted overall score
        overall_score = (
            credit_component * 0.30 +
            income_component * 0.25 +
            stability_component * 0.25 +
            tenure_component * 0.10 +
            loan_component * 0.10
        )
        
        # Determine conversion likelihood
        if overall_score >= 80:
            likelihood = "Very High"
            recommendation = "PRIORITY: Immediate outreach recommended. Customer is excellent prospect."
        elif overall_score >= 70:
            likelihood = "High"
            recommendation = "HIGH PRIORITY: Strong candidate for loan conversion."
        elif overall_score >= 60:
            likelihood = "Medium"
            recommendation = "GOOD PROSPECT: Consider for targeted outreach campaign."
        elif overall_score >= 50:
            likelihood = "Low-Medium"
            recommendation = "POTENTIAL: May convert with personalized offer."
        else:
            likelihood = "Low"
            recommendation = "MINIMAL: Lower conversion probability. Monitor for future opportunities."
        
        return {
            "success": True,
            "data": {
                "customer_id": customer_id,
                "overall_conversion_score": round(overall_score, 2),
                "conversion_likelihood": likelihood,
                "recommendation": recommendation,
                "score_breakdown": {
                    "credit_score_component": {
                        "weight": "30%",
                        "customer_credit": credit_score,
                        "score": round(credit_component, 2)
                    },
                    "income_component": {
                        "weight": "25%",
                        "annual_income": float(annual_income),
                        "score": round(income_component, 2)
                    },
                    "transaction_stability": {
                        "weight": "25%",
                        "stability_score": stability.get('stability_score', 0),
                        "score": round(stability_component, 2)
                    },
                    "account_tenure": {
                        "weight": "10%",
                        "months": tenure_months,
                        "score": round(tenure_component, 2)
                    },
                    "loan_behavior": {
                        "weight": "10%",
                        "active_loans": len(active_loans),
                        "default_history": has_default,
                        "score": round(loan_component, 2)
                    }
                },
                "risk_factors": {
                    "low_credit_score": credit_score < 650,
                    "low_income": annual_income < 300000,
                    "poor_stability": stability.get('stability_score', 0) < 50,
                    "short_tenure": tenure_months < 6,
                    "default_history": has_default
                }
            }
        }
    
    @staticmethod
    def get_recommended_products(customer_id: int) -> Dict[str, Any]:
        """
        Tool: Get recommended loan products for customer
        
        Input: customer_id (int)
        Output: List of suitable products ranked by fit
        """
        customer = customer_repo.get_customer_by_id(customer_id)
        if not customer:
            return {
                "success": False,
                "error": f"Customer {customer_id} not found",
                "data": None
            }
        
        annual_income = float(customer['annual_income']) or 0
        credit_score = customer['credit_score'] or 0
        account_tenure = customer['account_tenure_months'] or 0
        
        # Get eligible products
        eligible_products = product_repo.get_eligible_products(annual_income, credit_score, account_tenure)
        
        if not eligible_products:
            return {
                "success": True,
                "data": {
                    "customer_id": customer_id,
                    "recommendations": [],
                    "message": "Customer does not meet eligibility criteria for any current products"
                }
            }
        
        # Get transaction analysis for personalization
        category_breakdown = transaction_repo.get_category_breakdown(customer_id, 6)
        
        # Rank products based on customer profile
        recommendations = []
        for product in eligible_products:
            # Convert Decimal values to float for calculations
            interest_rate_min = float(product['interest_rate_min'])
            interest_rate_max = float(product['interest_rate_max'])
            min_loan = float(product['min_loan_amount'])
            max_loan = float(product['max_loan_amount'])
            tenure = int(product['tenure_months'])
            
            # Calculate product fit score
            if product['eligibility_status'] == 'Fully Eligible':
                rank_score = 100
            else:
                rank_score = 70
            
            # Adjust based on interest rates offered
            rate_range = interest_rate_max - interest_rate_min
            estimated_rate = interest_rate_min + (rate_range * (100 - credit_score) / 250)
            estimated_rate = min(max(estimated_rate, interest_rate_min), interest_rate_max)
            
            recommended_amount = float(min(max_loan, max(min_loan, annual_income * 0.2)))
            
            # Calculate monthly EMI using standard formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1)
            # where r = monthly interest rate (as decimal), n = tenure in months, P = principal
            monthly_rate = estimated_rate / 100 / 12 if estimated_rate > 0 else 0
            if monthly_rate > 0 and tenure > 0:
                emi = recommended_amount * monthly_rate * ((1 + monthly_rate) ** tenure) / (((1 + monthly_rate) ** tenure) - 1)
            else:
                emi = 0
            
            recommendations.append({
                "product_id": product['id'],
                "product_name": product['product_name'],
                "product_type": product['product_type'],
                "eligibility": product['eligibility_status'],
                "estimated_rate": round(estimated_rate, 2),
                "tenure_months": tenure,
                "loan_range": {
                    "min": min_loan,
                    "max": max_loan
                },
                "recommended_amount": round(recommended_amount, 2),
                "monthly_emi_estimate": round(emi, 2),
                "use_case": product['use_case'],
                "marketing_tagline": product['marketing_tagline'],
                "rank_score": rank_score
            })
        
        # Sort by rank score and interest rate
        recommendations.sort(key=lambda x: (-x['rank_score'], x['estimated_rate']))
        
        return {
            "success": True,
            "data": {
                "customer_id": customer_id,
                "recommendations": recommendations[:3],  # Top 3 recommendations
                "total_eligible_products": len(eligible_products),
                "personalization_note": "Products ranked by eligibility and estimated interest rates"
            }
        }
    
    @staticmethod
    def generate_outreach_message(customer_id: int, product_id: int) -> Dict[str, Any]:
        """
        Tool: Generate personalized outreach message for customer
        
        Input: customer_id (int), product_id (int)
        Output: Personalized WhatsApp-ready message
        """
        customer = customer_repo.get_customer_by_id(customer_id)
        if not customer:
            return {
                "success": False,
                "error": f"Customer {customer_id} not found",
                "data": None
            }
        
        product = product_repo.get_product_by_id(product_id)
        if not product:
            return {
                "success": False,
                "error": f"Product {product_id} not found",
                "data": None
            }
        
        # Get conversion score for personalization
        conversion_result = CRMTools.calculate_conversion_score(customer_id)
        conversion_score = conversion_result['data']['overall_conversion_score'] if conversion_result['success'] else 0
        
        # Get product recommendations for context
        rec_result = CRMTools.get_recommended_products(customer_id)
        estimated_rate = None
        if rec_result['success'] and rec_result['data']['recommendations']:
            for rec in rec_result['data']['recommendations']:
                if rec['product_id'] == product_id:
                    estimated_rate = rec['estimated_rate']
                    estimated_amount = rec['recommended_amount']
                    estimated_emi = rec['monthly_emi_estimate']
                    break
        
        # Get transaction analysis for personalization
        trans_result = CRMTools.analyze_transactions(customer_id, 6)
        category_breakdown = trans_result['data']['category_breakdown'] if trans_result['success'] else []
        
        # Build personalized message
        first_name = customer['first_name']
        product_name = product['product_name']
        tagline = product['marketing_tagline']
        
        # Personalize based on transaction patterns
        if category_breakdown:
            top_category = max(category_breakdown, key=lambda x: x['total_amount'])
            spending_context = f"Given your active spending in {top_category['product_category'].lower()}, "
        else:
            spending_context = ""
        
        # Create personalized message variations
        if conversion_score >= 80:
            tone = "EXCLUSIVE"
            message = f"Hi {first_name}! 🎉 Exclusive offer: {product_name} at just {estimated_rate}% p.a. {spending_context}{tagline}. Eligible amount: ₹{estimated_amount:,.0f}. EMI starts at ₹{estimated_emi:,.0f}/month. Call us on 1800-XXX-XXXX or reply YES to apply now! #BankingForYou"
        elif conversion_score >= 70:
            tone = "PERSONALIZED"
            message = f"Hi {first_name}! We have a special {product_name} offer for you. {spending_context}{tagline} Competitive rate of {estimated_rate}% p.a. Eligible amount: ₹{estimated_amount:,.0f}. Ready to apply? Reply with your preferred amount! #SpecialOffer"
        else:
            tone = "INFORMATIVE"
            message = f"Hi {first_name}! Interested in a {product_name}? {tagline} We can offer you ₹{estimated_amount:,.0f} at {estimated_rate}% p.a. with easy EMI options starting ₹{estimated_emi:,.0f}/month. Learn more: [Link] #PersonalLoan"
        
        # Ensure message is within WhatsApp character limits
        if len(message) > 160:
            # Create SMS version (shorter)
            sms_message = f"Hi {first_name}! Special {product_name} offer: {estimated_rate}% p.a., up to ₹{estimated_amount:,.0f}. EMI from ₹{estimated_emi:,.0f}/month. Reply YES or call 1800-XXX-XXXX."
        else:
            sms_message = message
        
        return {
            "success": True,
            "data": {
                "customer_id": customer_id,
                "customer_name": first_name,
                "product_name": product_name,
                "product_id": product_id,
                "conversion_score": round(conversion_score, 2),
                "tone": tone,
                "messages": {
                    "whatsapp": message,
                    "sms": sms_message,
                    "email_subject": f"{tone}: Your Personalized {product_name} Offer",
                    "character_count": len(message),
                    "fit_for_whatsapp": len(message) <= 4096
                },
                "offer_details": {
                    "estimated_rate": estimated_rate,
                    "eligible_amount": estimated_amount,
                    "monthly_emi": estimated_emi,
                    "validity_days": 30
                }
            }
        }
    
    @staticmethod
    def identify_high_value_prospects() -> Dict[str, Any]:
        """
        Tool: Identify top high-value customers for personal loan offers
        
        Input: None
        Output: Ranked list of high-value prospects
        """
        # Get high-value customers
        prospects = customer_repo.get_high_value_customers(min_income=500000, min_credit_score=700)
        
        if not prospects:
            return {
                "success": False,
                "error": "No high-value customers found",
                "data": None
            }
        
        # Score and rank each prospect
        ranked_prospects = []
        for prospect in prospects:
            conversion_result = CRMTools.calculate_conversion_score(prospect['id'])
            
            if conversion_result['success']:
                conversion_score = conversion_result['data']['overall_conversion_score']
                ranked_prospects.append({
                    "customer_id": prospect['id'],
                    "name": f"{prospect['first_name']} {prospect['last_name']}",
                    "email": prospect['email'],
                    "phone": prospect['phone'],
                    "segment": prospect.get('segment_name', 'Unknown'),
                    "annual_income": float(prospect['annual_income']),
                    "credit_score": prospect['credit_score'],
                    "account_tenure_months": prospect['account_tenure_months'],
                    "transaction_count_6m": prospect.get('transaction_count_6m', 0),
                    "conversion_score": round(conversion_score, 2),
                    "conversion_likelihood": conversion_result['data']['conversion_likelihood'],
                    "priority": "IMMEDIATE" if conversion_score >= 80 else "HIGH" if conversion_score >= 70 else "MEDIUM"
                })
        
        # Sort by conversion score
        ranked_prospects.sort(key=lambda x: -x['conversion_score'])
        
        # Get top 10
        top_prospects = ranked_prospects[:10]
        
        return {
            "success": True,
            "data": {
                "total_high_value_customers": len(prospects),
                "prospects_analyzed": len(ranked_prospects),
                "top_prospects": top_prospects,
                "summary": {
                    "immediate_priority": len([p for p in top_prospects if p['priority'] == 'IMMEDIATE']),
                    "high_priority": len([p for p in top_prospects if p['priority'] == 'HIGH']),
                    "medium_priority": len([p for p in top_prospects if p['priority'] == 'MEDIUM'])
                }
            }
        }
    
    @staticmethod
    def identify_low_value_prospects() -> Dict[str, Any]:
        """
        Tool: Identify low-value customers with lower conversion scores for recovery/engagement strategies
        
        Input: None
        Output: Ranked list of low-value prospects for recovery campaigns
        """
        # Get all active customers
        all_customers = customer_repo.get_all_active_customers()
        
        if not all_customers:
            return {
                "success": False,
                "error": "No customers found",
                "data": None
            }
        
        # Score each customer and identify low-value ones
        scored_customers = []
        for customer in all_customers:
            try:
                conversion_result = CRMTools.calculate_conversion_score(customer['id'])
                
                if conversion_result['success']:
                    conversion_score = conversion_result['data']['overall_conversion_score']
                    scored_customers.append({
                        "customer_id": customer['id'],
                        "name": f"{customer['first_name']} {customer['last_name']}",
                        "email": customer.get('email', 'N/A'),
                        "phone": customer.get('phone', 'N/A'),
                        "segment": customer.get('segment_name', 'Unknown'),
                        "annual_income": float(customer['annual_income']),
                        "credit_score": customer['credit_score'],
                        "account_tenure_months": customer['account_tenure_months'],
                        "conversion_score": round(conversion_score, 2),
                        "conversion_likelihood": conversion_result['data']['conversion_likelihood'],
                        "recovery_priority": "CRITICAL" if conversion_score < 20 else "HIGH" if conversion_score < 40 else "MEDIUM"
                    })
            except Exception as e:
                # Skip customers that fail scoring
                pass
        
        # Sort by conversion score (ascending - lowest first)
        scored_customers.sort(key=lambda x: x['conversion_score'])
        
        # Get bottom 10 lowest-value prospects
        bottom_prospects = scored_customers[:10]
        
        return {
            "success": True,
            "data": {
                "total_customers_analyzed": len(all_customers),
                "low_value_customers_found": len(scored_customers),
                "bottom_prospects": bottom_prospects,
                "summary": {
                    "critical_priority": len([p for p in bottom_prospects if p['recovery_priority'] == 'CRITICAL']),
                    "high_priority": len([p for p in bottom_prospects if p['recovery_priority'] == 'HIGH']),
                    "medium_priority": len([p for p in bottom_prospects if p['recovery_priority'] == 'MEDIUM'])
                }
            }
        }


# Tool registry for MCP server
TOOLS = {
    "get_customer_profile": {
        "description": "Fetch complete customer profile including financial and account information",
        "function": CRMTools.get_customer_profile,
        "parameters": {
            "customer_id": {
                "type": "integer",
                "description": "The customer ID"
            }
        }
    },
    "analyze_transactions": {
        "description": "Analyze customer transaction patterns for last N months",
        "function": CRMTools.analyze_transactions,
        "parameters": {
            "customer_id": {
                "type": "integer",
                "description": "The customer ID"
            },
            "months": {
                "type": "integer",
                "description": "Number of months to analyze (default: 6)",
                "default": 6
            }
        }
    },
    "calculate_conversion_score": {
        "description": "Calculate likelihood of loan conversion for a customer (0-100)",
        "function": CRMTools.calculate_conversion_score,
        "parameters": {
            "customer_id": {
                "type": "integer",
                "description": "The customer ID"
            }
        }
    },
    "get_recommended_products": {
        "description": "Get list of recommended loan products for a customer",
        "function": CRMTools.get_recommended_products,
        "parameters": {
            "customer_id": {
                "type": "integer",
                "description": "The customer ID"
            }
        }
    },
    "generate_outreach_message": {
        "description": "Generate personalized outreach message for a customer product offer",
        "function": CRMTools.generate_outreach_message,
        "parameters": {
            "customer_id": {
                "type": "integer",
                "description": "The customer ID"
            },
            "product_id": {
                "type": "integer",
                "description": "The product ID"
            }
        }
    },
    "identify_high_value_prospects": {
        "description": "Identify and rank top high-value customers for personal loan offers",
        "function": CRMTools.identify_high_value_prospects,
        "parameters": {}
    },
    "identify_low_value_prospects": {
        "description": "Identify and rank low-value customers for recovery and engagement strategies",
        "function": CRMTools.identify_low_value_prospects,
        "parameters": {}
    }
}
