"""
Customer Repository - Database access for customers
"""
from typing import List, Dict, Any, Optional
from config.database import db, tuple_to_dict


class CustomerRepository:
    """Access and manage customer data"""
    
    # Column names for get_customer_by_id query
    CUSTOMER_COLUMNS = [
        'id', 'first_name', 'last_name', 'email', 'phone', 'annual_income',
        'credit_score', 'employment_status', 'employment_type', 'account_tenure_months',
        'account_status', 'last_transaction_date', 'total_deposits', 'total_withdrawals',
        'segment_name', 'created_at'
    ]
    
    @staticmethod
    def get_customer_by_id(customer_id: int) -> Dict[str, Any]:
        """Get customer details by ID"""
        query = """
        SELECT 
            c.id,
            c.first_name,
            c.last_name,
            c.email,
            c.phone,
            c.annual_income,
            c.credit_score,
            c.employment_status,
            c.employment_type,
            c.account_tenure_months,
            c.account_status,
            c.last_transaction_date,
            c.total_deposits,
            c.total_withdrawals,
            cs.segment_name,
            c.created_at
        FROM customers c
        LEFT JOIN customer_segments cs ON c.segment_id = cs.id
        WHERE c.id = %s
        """
        result = db.execute_single(query, (customer_id,))
        return tuple_to_dict(CustomerRepository.CUSTOMER_COLUMNS, result) if result else {}
    
    @staticmethod
    def get_all_active_customers() -> List[Dict[str, Any]]:
        """Get all active customers"""
        query = """
        SELECT 
            c.id,
            c.first_name,
            c.last_name,
            c.email,
            c.annual_income,
            c.credit_score,
            c.account_tenure_months,
            c.account_status,
            c.last_transaction_date,
            cs.segment_name
        FROM customers c
        LEFT JOIN customer_segments cs ON c.segment_id = cs.id
        WHERE c.account_status = 'Active'
        ORDER BY c.annual_income DESC
        """
        active_cols = ['id', 'first_name', 'last_name', 'email', 'annual_income', 'credit_score', 'account_tenure_months', 'account_status', 'last_transaction_date', 'segment_name']
        rows = db.execute_query(query)
        return [tuple_to_dict(active_cols, row) for row in rows]
    
    @staticmethod
    def get_high_value_customers(min_income: int = 500000, min_credit_score: int = 700) -> List[Dict[str, Any]]:
        """Get high-value customers matching criteria"""
        query = """
        SELECT 
            c.id,
            c.first_name,
            c.last_name,
            c.email,
            c.phone,
            c.annual_income,
            c.credit_score,
            c.account_tenure_months,
            c.employment_type,
            cs.segment_name,
            COUNT(t.id) as transaction_count_6m,
            SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END) as total_credits,
            SUM(CASE WHEN t.transaction_type = 'debit' THEN t.amount ELSE 0 END) as total_debits
        FROM customers c
        LEFT JOIN customer_segments cs ON c.segment_id = cs.id
        LEFT JOIN transactions t ON c.id = t.customer_id 
            AND t.transaction_date >= CURRENT_DATE - INTERVAL '6 months'
        WHERE c.account_status = 'Active' 
            AND c.annual_income >= %s
            AND c.credit_score >= %s
        GROUP BY c.id, c.first_name, c.last_name, c.email, c.phone, c.annual_income, 
                 c.credit_score, c.account_tenure_months, c.employment_type, cs.segment_name
        ORDER BY c.annual_income DESC, c.credit_score DESC
        """
        hvc_cols = ['id', 'first_name', 'last_name', 'email', 'phone', 'annual_income', 'credit_score', 'account_tenure_months', 'employment_type', 'segment_name', 'transaction_count_6m', 'total_credits', 'total_debits']
        rows = db.execute_query(query, (min_income, min_credit_score))
        return [tuple_to_dict(hvc_cols, row) for row in rows]
    
    @staticmethod
    def get_customers_by_segment(segment_name: str) -> List[Dict[str, Any]]:
        """Get customers by segment"""
        query = """
        SELECT 
            c.id,
            c.first_name,
            c.last_name,
            c.email,
            c.annual_income,
            c.credit_score,
            cs.segment_name
        FROM customers c
        LEFT JOIN customer_segments cs ON c.segment_id = cs.id
        WHERE cs.segment_name = %s AND c.account_status = 'Active'
        ORDER BY c.annual_income DESC
        """
        seg_cols = ['id', 'first_name', 'last_name', 'email', 'annual_income', 'credit_score', 'segment_name']
        rows = db.execute_query(query, (segment_name,))
        return [tuple_to_dict(seg_cols, row) for row in rows]
    
    @staticmethod
    def search_customers(search_term: str) -> List[Dict[str, Any]]:
        """Search customers by name or email"""
        query = """
        SELECT 
            c.id,
            c.first_name,
            c.last_name,
            c.email,
            c.annual_income,
            c.credit_score,
            cs.segment_name
        FROM customers c
        LEFT JOIN customer_segments cs ON c.segment_id = cs.id
        WHERE c.account_status = 'Active' 
            AND (c.first_name ILIKE %s OR c.last_name ILIKE %s OR c.email ILIKE %s)
        ORDER BY c.annual_income DESC
        """
        search_cols = ['id', 'first_name', 'last_name', 'email', 'annual_income', 'credit_score', 'segment_name']
        search_param = f"%{search_term}%"
        rows = db.execute_query(query, (search_param, search_param, search_param))
        return [tuple_to_dict(search_cols, row) for row in rows]


# Singleton instance
customer_repo = CustomerRepository()
