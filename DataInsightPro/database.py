import sqlite3
import pandas as pd
import os
import tempfile
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """Manages SQLite database operations for the data analysis tool."""
    
    def __init__(self, db_path: str = ":memory:"):
        """Initialize database manager with in-memory database by default."""
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.execute("PRAGMA foreign_keys = ON")
        
    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str) -> None:
        """Create a table from a pandas DataFrame."""
        try:
            # Clean table name
            clean_table_name = self._clean_table_name(table_name)
            
            # Drop table if exists
            self.connection.execute(f"DROP TABLE IF EXISTS {clean_table_name}")
            
            # Create table from DataFrame
            df.to_sql(clean_table_name, self.connection, index=False, if_exists='replace')
            self.connection.commit()
            
        except Exception as e:
            raise Exception(f"Error creating table from DataFrame: {str(e)}")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame."""
        try:
            result_df = pd.read_sql_query(query, self.connection)
            return result_df
        except Exception as e:
            raise Exception(f"Error executing query: {str(e)}")
    
    def get_table_names(self) -> List[str]:
        """Get list of all table names in the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        except Exception as e:
            raise Exception(f"Error getting table names: {str(e)}")
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get column names for a specific table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            return columns
        except Exception as e:
            raise Exception(f"Error getting table columns: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get detailed schema information for a table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema_info = cursor.fetchall()
            
            schema = {
                'table_name': table_name,
                'columns': []
            }
            
            for col_info in schema_info:
                column = {
                    'name': col_info[1],
                    'type': col_info[2],
                    'not_null': bool(col_info[3]),
                    'primary_key': bool(col_info[5])
                }
                schema['columns'].append(column)
            
            # Get sample data for context
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_data = cursor.fetchall()
            schema['sample_data'] = sample_data
            
            return schema
        except Exception as e:
            raise Exception(f"Error getting table schema: {str(e)}")
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get comprehensive information about a table."""
        try:
            # Get basic info
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get column info
            columns = self.get_table_columns(table_name)
            
            # Get data types and sample values
            column_info = []
            for col in columns:
                cursor.execute(f"SELECT DISTINCT typeof({col}) FROM {table_name} LIMIT 5")
                data_types = [row[0] for row in cursor.fetchall()]
                
                cursor.execute(f"SELECT {col} FROM {table_name} WHERE {col} IS NOT NULL LIMIT 3")
                sample_values = [row[0] for row in cursor.fetchall()]
                
                column_info.append({
                    'name': col,
                    'data_types': data_types,
                    'sample_values': sample_values
                })
            
            return {
                'table_name': table_name,
                'row_count': row_count,
                'column_count': len(columns),
                'columns': column_info
            }
        except Exception as e:
            raise Exception(f"Error getting table info: {str(e)}")
    
    def _clean_table_name(self, table_name: str) -> str:
        """Clean table name to be SQL-safe."""
        # Remove file extension and special characters
        clean_name = table_name.replace('.csv', '').replace('.xlsx', '').replace('.xls', '')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        
        # Ensure it starts with a letter
        if not clean_name[0].isalpha():
            clean_name = 'table_' + clean_name
        
        return clean_name
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()
