"""
Database Configuration and Connection Manager
"""
import pg8000
from typing import List, Dict, Any
import os
from datetime import datetime, timedelta

# Database connection parameters
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "banking_crm"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}


def tuple_to_dict(columns: List[str], row: tuple) -> Dict[str, Any]:
    """Convert tuple row to dict using column names"""
    return dict(zip(columns, row)) if row else {}


class DatabaseConnection:
    """Manages PostgreSQL connections using pg8000 (pure Python driver)"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            # Use pg8000.connect with keyword arguments
            self.connection = pg8000.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                database=DB_CONFIG['database'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password']
            )
            print(f"✓ Connected to PostgreSQL: {DB_CONFIG['database']}")
            return self.connection
        except Exception as e:
            print(f"✗ Database connection failed: {str(e)}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✓ Disconnected from PostgreSQL")
    
    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Execute SELECT query and return results as list of tuples"""
        try:
            if not self.connection:
                self.connect()
            
            # Use pg8000 native parameter style (format = %s)
            # Don't convert - pg8000 expects %s for the cursor interface
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            rows = cursor.fetchall()
            
            # pg8000 returns a tuple of lists - convert to list of tuples
            if isinstance(rows, tuple):
                rows = [tuple(row) if isinstance(row, list) else row for row in rows]
            
            return rows if rows else []
        except Exception as e:
            # Rollback transaction on error to recover from aborted state
            try:
                self.connection.rollback()
            except:
                pass
            print(f"✗ Query execution failed: {str(e)}")
            return []
    
    def execute_single(self, query: str, params: tuple = None) -> Any:
        """Execute SELECT query and return single result (as tuple)"""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_count(self, query: str, params: tuple = None) -> int:
        """Execute COUNT query and return count"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            # Rollback transaction on error
            try:
                self.connection.rollback()
            except:
                pass
            print(f"✗ Count query failed: {str(e)}")
            return 0


# Global database instance
db = DatabaseConnection()
