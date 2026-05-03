"""
Transaction Repository - Database access for transactions
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from config.database import db, tuple_to_dict


class TransactionRepository:
    """Access and manage transaction data"""
    
    # Column names for tuple conversion
    TRANSACTION_COLUMNS = [
        'id', 'customer_id', 'transaction_date', 'transaction_time', 'amount',
        'transaction_type', 'description', 'product_category', 'merchant_category',
        'channel', 'transaction_status'
    ]
    
    PATTERN_COLUMNS = [
        'total_transactions', 'transaction_days', 'total_credits', 'total_debits',
        'avg_transaction_amount', 'max_transaction_amount', 'min_transaction_amount',
        'stddev_amount', 'active_months', 'last_transaction_date'
    ]
    
    CATEGORY_BREAKDOWN_COLUMNS = [
        'product_category', 'transaction_count', 'total_amount', 'avg_amount', 'percentage'
    ]
    
    MONTHLY_TREND_COLUMNS = [
        'month', 'transaction_count', 'monthly_credits', 'monthly_debits', 'total_amount'
    ]
    
    @staticmethod
    def get_customer_transactions(customer_id: int, months: int = 6) -> List[Dict[str, Any]]:
        """Get customer transactions for last N months"""
        query = f"""
        SELECT 
            id,
            customer_id,
            transaction_date,
            transaction_time,
            amount,
            transaction_type,
            description,
            product_category,
            merchant_category,
            channel,
            transaction_status
        FROM transactions
        WHERE customer_id = %s 
            AND transaction_date >= CURRENT_DATE - INTERVAL '{months} months'
        ORDER BY transaction_date DESC
        """
        rows = db.execute_query(query, (customer_id,))
        return [tuple_to_dict(TransactionRepository.TRANSACTION_COLUMNS, row) for row in rows]
    
    @staticmethod
    def analyze_transaction_patterns(customer_id: int, months: int = 6) -> Dict[str, Any]:
        """Analyze customer transaction patterns"""
        query = f"""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT transaction_date) as transaction_days,
            SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as total_credits,
            SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as total_debits,
            AVG(amount) as avg_transaction_amount,
            MAX(amount) as max_transaction_amount,
            MIN(amount) as min_transaction_amount,
            STDDEV(amount) as stddev_amount,
            COUNT(DISTINCT EXTRACT(MONTH FROM transaction_date)) as active_months,
            MAX(transaction_date) as last_transaction_date
        FROM transactions
        WHERE customer_id = %s 
            AND transaction_date >= CURRENT_DATE - INTERVAL '{months} months'
            AND transaction_status = 'Completed'
        """
        result = db.execute_single(query, (customer_id,))
        return tuple_to_dict(TransactionRepository.PATTERN_COLUMNS, result) if result else {}
    
    @staticmethod
    def get_category_breakdown(customer_id: int, months: int = 6) -> List[Dict[str, Any]]:
        """Get spending breakdown by category"""
        query = f"""
        SELECT 
            product_category,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            ROUND(100.0 * SUM(amount) / 
                (SELECT SUM(amount) FROM transactions 
                 WHERE customer_id = %s 
                   AND transaction_date >= CURRENT_DATE - INTERVAL '{months} months'
                   AND transaction_status = 'Completed'), 2) as percentage
        FROM transactions
        WHERE customer_id = %s 
            AND transaction_date >= CURRENT_DATE - INTERVAL '{months} months'
            AND transaction_status = 'Completed'
        GROUP BY product_category
        ORDER BY total_amount DESC
        """
        rows = db.execute_query(query, (customer_id, customer_id))
        return [tuple_to_dict(TransactionRepository.CATEGORY_BREAKDOWN_COLUMNS, row) for row in rows]
    
    @staticmethod
    def get_monthly_transaction_trend(customer_id: int, months: int = 6) -> List[Dict[str, Any]]:
        """Get monthly transaction trend"""
        query = f"""
        SELECT 
            TO_CHAR(transaction_date, 'YYYY-MM') as month,
            COUNT(*) as transaction_count,
            SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as monthly_credits,
            SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as monthly_debits,
            SUM(amount) as total_amount
        FROM transactions
        WHERE customer_id = %s 
            AND transaction_date >= CURRENT_DATE - INTERVAL '{months} months'
            AND transaction_status = 'Completed'
        GROUP BY TO_CHAR(transaction_date, 'YYYY-MM')
        ORDER BY month DESC
        """
        rows = db.execute_query(query, (customer_id,))
        return [tuple_to_dict(TransactionRepository.MONTHLY_TREND_COLUMNS, row) for row in rows]
    
    @staticmethod
    def calculate_stability_score(customer_id: int, months: int = 6) -> Dict[str, Any]:
        """Calculate transaction stability score"""
        patterns = TransactionRepository.analyze_transaction_patterns(customer_id, months)
        
        if not patterns or patterns.get('total_transactions', 0) == 0:
            return {
                "stability_score": 0,
                "consistency": "No Activity",
                "frequency": "None",
                "reliability": "Unknown"
            }
        
        # Convert Decimal values to float for calculations
        total_txns = float(patterns.get('total_transactions', 0))
        active_months = int(patterns.get('active_months', 0) or 0)
        avg_amount = float(patterns.get('avg_transaction_amount', 0) or 0)
        stddev = float(patterns.get('stddev_amount', 0) or 0)
        total_credits = float(patterns.get('total_credits', 0) or 0)
        total_debits = float(patterns.get('total_debits', 0) or 0)
        
        # Stability score based on frequency, consistency, and regularity
        frequency_score = min((total_txns / (months * 5)) * 100, 100)  # ~5 txns/month = 100
        consistency_score = 100 - min((stddev / (avg_amount + 1)) * 50, 100) if avg_amount > 0 else 50
        regularity_score = (active_months / months) * 100 if months > 0 else 0
        
        overall_score = (frequency_score * 0.4 + consistency_score * 0.35 + regularity_score * 0.25)
        
        return {
            "stability_score": round(overall_score, 2),
            "transaction_frequency": int(total_txns),
            "active_months": active_months,
            "avg_monthly_txns": round(total_txns / months, 2) if months > 0 else 0,
            "consistency": "High" if consistency_score > 70 else "Medium" if consistency_score > 40 else "Low",
            "regularity": "Regular" if active_months >= months - 1 else "Inconsistent",
            "avg_amount": round(avg_amount, 2),
            "total_volume": round(total_credits + total_debits, 2)
        }


# Singleton instance
transaction_repo = TransactionRepository()
