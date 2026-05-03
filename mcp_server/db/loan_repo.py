"""
Loan Repository - Database access for customer loans and offers
"""
from typing import List, Dict, Any
from config.database import db, tuple_to_dict


class LoanRepository:
    """Access and manage loan and offer data"""
    
    # Column names for active loans query
    ACTIVE_LOANS_COLUMNS = [
        'id', 'product_id', 'product_name', 'product_type', 'loan_amount',
        'interest_rate', 'tenure_months', 'start_date', 'end_date', 
        'product_status', 'emi_amount', 'months_remaining'
    ]
    
    LOAN_HISTORY_COLUMNS = [
        'id', 'product_name', 'product_type', 'loan_amount', 'interest_rate',
        'tenure_months', 'start_date', 'end_date', 'product_status', 'emi_amount'
    ]
    
    @staticmethod
    def get_customer_active_loans(customer_id: int) -> List[Dict[str, Any]]:
        """Get customer's active loans"""
        query = """
        SELECT 
            cp.id,
            cp.product_id,
            p.product_name,
            p.product_type,
            cp.loan_amount,
            cp.interest_rate,
            cp.tenure_months,
            cp.start_date,
            cp.end_date,
            cp.product_status,
            cp.emi_amount,
            ROUND((cp.end_date - CURRENT_DATE) / 30.0, 1) as months_remaining
        FROM customer_products cp
        JOIN products p ON cp.product_id = p.id
        WHERE cp.customer_id = %s AND cp.product_status = 'Active'
        ORDER BY cp.start_date DESC
        """
        rows = db.execute_query(query, (customer_id,))
        return [tuple_to_dict(LoanRepository.ACTIVE_LOANS_COLUMNS, row) for row in rows]
    
    @staticmethod
    def get_customer_loan_history(customer_id: int) -> List[Dict[str, Any]]:
        """Get customer's complete loan history"""
        query = """
        SELECT 
            cp.id,
            p.product_name,
            p.product_type,
            cp.loan_amount,
            cp.interest_rate,
            cp.tenure_months,
            cp.start_date,
            cp.end_date,
            cp.product_status,
            cp.emi_amount
        FROM customer_products cp
        JOIN products p ON cp.product_id = p.id
        WHERE cp.customer_id = %s
        ORDER BY cp.start_date DESC
        """
        rows = db.execute_query(query, (customer_id,))
        return [tuple_to_dict(LoanRepository.LOAN_HISTORY_COLUMNS, row) for row in rows]
    
    @staticmethod
    def has_default_history(customer_id: int) -> bool:
        """Check if customer has any defaulted loans"""
        query = """
        SELECT COUNT(*) as defaulted_count
        FROM customer_products
        WHERE customer_id = %s AND product_status = 'Defaulted'
        """
        result = db.execute_single(query, (customer_id,))
        if result:
            result_dict = tuple_to_dict(['defaulted_count'], result) if isinstance(result, tuple) else result
            return result_dict.get('defaulted_count', 0) > 0
        return False
    
    @staticmethod
    def create_loan_offer(customer_id: int, product_id: int, conversion_score: float,
                         offer_amount: float, offered_rate: float, 
                         outreach_message: str, outreach_channel: str) -> Dict[str, Any]:
        """Create a new loan offer (placeholder for future implementation)"""
        # This feature is deferred for future implementation
        # Currently, messages are generated but not stored in DB
        return {
            "status": "success",
            "message": "Offer created (storage deferred)"
        }
    
    @staticmethod
    def get_recent_offers(customer_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent loan offers for customer"""
        query = """
        SELECT 
            lo.id,
            p.product_name,
            lo.conversion_score,
            lo.offer_amount,
            lo.offered_rate,
            lo.outreach_channel,
            lo.offer_status,
            lo.created_at,
            lo.offer_valid_until
        FROM loan_offers lo
        JOIN products p ON lo.product_id = p.id
        WHERE lo.customer_id = %s
        ORDER BY lo.created_at DESC
        LIMIT %s
        """
        return db.execute_query(query, (customer_id, limit))


# Singleton instance
loan_repo = LoanRepository()
