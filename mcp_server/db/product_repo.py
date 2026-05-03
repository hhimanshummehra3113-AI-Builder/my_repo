"""
Product Repository - Database access for products
"""
from typing import List, Dict, Any
from config.database import db, tuple_to_dict


class ProductRepository:
    """Access and manage product data"""
    
    # Column names for tuple conversion
    PRODUCT_COLUMNS = [
        'id', 'product_name', 'product_type', 'min_annual_income',
        'min_credit_score', 'min_account_tenure_months', 'min_loan_amount',
        'max_loan_amount', 'interest_rate_min', 'interest_rate_max',
        'tenure_months', 'use_case', 'marketing_tagline', 'description'
    ]
    
    ELIGIBLE_PRODUCT_COLUMNS = [
        'id', 'product_name', 'product_type', 'min_annual_income',
        'min_credit_score', 'min_account_tenure_months', 'min_loan_amount',
        'max_loan_amount', 'interest_rate_min', 'interest_rate_max',
        'tenure_months', 'use_case', 'marketing_tagline', 'description',
        'eligibility_status'
    ]
    
    PRODUCT_TYPE_COLUMNS = [
        'id', 'product_name', 'product_type', 'min_annual_income',
        'min_credit_score', 'min_account_tenure_months', 'min_loan_amount',
        'max_loan_amount', 'interest_rate_min', 'interest_rate_max',
        'tenure_months', 'use_case', 'marketing_tagline'
    ]
    
    BEST_RATE_COLUMNS = [
        'id', 'product_name', 'product_type', 'interest_rate_min',
        'interest_rate_max', 'min_loan_amount', 'max_loan_amount',
        'tenure_months', 'marketing_tagline'
    ]
    
    @staticmethod
    def get_all_products() -> List[Dict[str, Any]]:
        """Get all loan products"""
        query = """
        SELECT 
            id,
            product_name,
            product_type,
            min_annual_income,
            min_credit_score,
            min_account_tenure_months,
            min_loan_amount,
            max_loan_amount,
            interest_rate_min,
            interest_rate_max,
            tenure_months,
            use_case,
            marketing_tagline,
            description
        FROM products
        ORDER BY product_name
        """
        rows = db.execute_query(query)
        return [tuple_to_dict(ProductRepository.PRODUCT_COLUMNS, row) for row in rows]
    
    @staticmethod
    def get_product_by_id(product_id: int) -> Dict[str, Any]:
        """Get product details by ID"""
        query = """
        SELECT 
            id,
            product_name,
            product_type,
            min_annual_income,
            min_credit_score,
            min_account_tenure_months,
            min_loan_amount,
            max_loan_amount,
            interest_rate_min,
            interest_rate_max,
            tenure_months,
            use_case,
            marketing_tagline,
            description
        FROM products
        WHERE id = %s
        """
        result = db.execute_single(query, (product_id,))
        return tuple_to_dict(ProductRepository.PRODUCT_COLUMNS, result) if result else {}
    
    @staticmethod
    def get_eligible_products(annual_income: float, credit_score: int, 
                             account_tenure: int) -> List[Dict[str, Any]]:
        """Get products customer is eligible for"""
        query = """
        SELECT 
            id,
            product_name,
            product_type,
            min_annual_income,
            min_credit_score,
            min_account_tenure_months,
            min_loan_amount,
            max_loan_amount,
            interest_rate_min,
            interest_rate_max,
            tenure_months,
            use_case,
            marketing_tagline,
            description,
            CASE 
                WHEN %s >= min_annual_income 
                    AND %s >= min_credit_score
                    AND %s >= min_account_tenure_months
                THEN 'Fully Eligible'
                WHEN %s >= min_annual_income * 0.8
                    AND %s >= min_credit_score - 50
                THEN 'Partially Eligible'
                ELSE 'Not Eligible'
            END as eligibility_status
        FROM products
        WHERE %s >= min_annual_income * 0.8
            AND %s >= min_credit_score - 50
        ORDER BY 
            CASE 
                WHEN %s >= min_annual_income 
                    AND %s >= min_credit_score
                    AND %s >= min_account_tenure_months
                THEN 1
                WHEN %s >= min_annual_income * 0.8
                    AND %s >= min_credit_score - 50
                THEN 2
                ELSE 3
            END,
            interest_rate_min ASC
        """
        rows = db.execute_query(query, (annual_income, credit_score, account_tenure,
                                         annual_income, credit_score,
                                         annual_income, credit_score,
                                         annual_income, credit_score, account_tenure,
                                         annual_income, credit_score))
        return [tuple_to_dict(ProductRepository.ELIGIBLE_PRODUCT_COLUMNS, row) for row in rows]
    
    @staticmethod
    def get_products_by_type(product_type: str) -> List[Dict[str, Any]]:
        """Get products by type (e.g., 'Personal Loan', 'Home Loan')"""
        query = """
        SELECT 
            id,
            product_name,
            product_type,
            min_annual_income,
            min_credit_score,
            min_account_tenure_months,
            min_loan_amount,
            max_loan_amount,
            interest_rate_min,
            interest_rate_max,
            tenure_months,
            use_case,
            marketing_tagline
        FROM products
        WHERE product_type = %s
        ORDER BY interest_rate_min ASC
        """
        rows = db.execute_query(query, (product_type,))
        return [tuple_to_dict(ProductRepository.PRODUCT_TYPE_COLUMNS, row) for row in rows]
    
    @staticmethod
    def get_best_rate_product(annual_income: float, credit_score: int) -> Dict[str, Any]:
        """Get product with best interest rate for customer"""
        query = """
        SELECT 
            id,
            product_name,
            product_type,
            interest_rate_min,
            interest_rate_max,
            min_loan_amount,
            max_loan_amount,
            tenure_months,
            marketing_tagline
        FROM products
        WHERE %s >= min_annual_income 
            AND %s >= min_credit_score
        ORDER BY interest_rate_min ASC
        LIMIT 1
        """
        result = db.execute_single(query, (annual_income, credit_score))
        return tuple_to_dict(ProductRepository.BEST_RATE_COLUMNS, result) if result else {}


# Singleton instance
product_repo = ProductRepository()
