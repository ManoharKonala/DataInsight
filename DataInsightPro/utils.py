import pandas as pd
import re
import io
from typing import Tuple, Any
import streamlit as st

def process_uploaded_file(uploaded_file) -> Tuple[pd.DataFrame, str]:
    """Process uploaded CSV or Excel file and return DataFrame and table name."""
    try:
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1].lower()
        
        # Generate table name from file name
        table_name = generate_table_name(file_name)
        
        # Read file based on extension
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Clean and validate DataFrame
        df = clean_dataframe(df)
        
        return df, table_name
        
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")

def generate_table_name(file_name: str) -> str:
    """Generate a SQL-safe table name from file name."""
    # Remove file extension
    table_name = file_name.rsplit('.', 1)[0]
    
    # Replace spaces and special characters with underscores
    table_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name)
    
    # Remove consecutive underscores
    table_name = re.sub(r'_+', '_', table_name)
    
    # Remove leading/trailing underscores
    table_name = table_name.strip('_')
    
    # Ensure it starts with a letter
    if not table_name[0].isalpha():
        table_name = 'table_' + table_name
    
    # Limit length
    if len(table_name) > 50:
        table_name = table_name[:50]
    
    return table_name.lower()

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare DataFrame for database storage."""
    # Make a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Clean column names
    df_clean.columns = [clean_column_name(col) for col in df_clean.columns]
    
    # Handle duplicate column names
    df_clean = handle_duplicate_columns(df_clean)
    
    # Convert data types appropriately
    df_clean = optimize_data_types(df_clean)
    
    # Handle missing values
    df_clean = handle_missing_values(df_clean)
    
    return df_clean

def clean_column_name(column_name: str) -> str:
    """Clean column name to be SQL-safe."""
    # Convert to string in case it's not
    col_name = str(column_name)
    
    # Replace spaces and special characters with underscores
    col_name = re.sub(r'[^a-zA-Z0-9_]', '_', col_name)
    
    # Remove consecutive underscores
    col_name = re.sub(r'_+', '_', col_name)
    
    # Remove leading/trailing underscores
    col_name = col_name.strip('_')
    
    # Ensure it starts with a letter
    if not col_name or not col_name[0].isalpha():
        col_name = 'col_' + col_name
    
    return col_name.lower()

def handle_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Handle duplicate column names by adding suffixes."""
    columns = df.columns.tolist()
    seen = {}
    new_columns = []
    
    for col in columns:
        if col in seen:
            seen[col] += 1
            new_columns.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_columns.append(col)
    
    df.columns = new_columns
    return df

def optimize_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize data types for better performance and storage."""
    for col in df.columns:
        # Skip if column is empty
        if df[col].isnull().all():
            continue
        
        # Try to convert to datetime
        if df[col].dtype == 'object':
            try:
                # Check if it looks like a date
                sample_values = df[col].dropna().head(10)
                if any(is_date_like(str(val)) for val in sample_values):
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass
        
        # Try to convert to numeric
        if df[col].dtype == 'object':
            try:
                # Try integer conversion first
                converted = pd.to_numeric(df[col], errors='coerce')
                if not converted.isnull().all():
                    # Check if all values are integers
                    if converted.dropna().apply(lambda x: x.is_integer()).all():
                        df[col] = converted.astype('Int64')  # Nullable integer
                    else:
                        df[col] = converted
            except:
                pass
    
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values appropriately."""
    # For now, keep missing values as is - let the user decide how to handle them
    # This prevents data loss and maintains data integrity
    return df

def is_date_like(value: str) -> bool:
    """Check if a string value looks like a date."""
    if not isinstance(value, str):
        return False
    
    # Common date patterns
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
        r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
    ]
    
    return any(re.match(pattern, value.strip()) for pattern in date_patterns)

def validate_sql_query(query: str) -> bool:
    """Basic SQL query validation."""
    if not query or not query.strip():
        return False
    
    query = query.strip().upper()
    
    # Check for dangerous operations
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER', 'TRUNCATE']
    for keyword in dangerous_keywords:
        if keyword in query:
            return False
    
    # Must start with SELECT
    if not query.startswith('SELECT'):
        return False
    
    return True

def format_query_result(df: pd.DataFrame) -> pd.DataFrame:
    """Format query result for display."""
    if df.empty:
        return df
    
    # Limit the number of rows displayed
    max_rows = 1000
    if len(df) > max_rows:
        st.warning(f"Showing first {max_rows} rows out of {len(df)} total rows.")
        df = df.head(max_rows)
    
    # Format numeric columns for better display
    for col in df.columns:
        if df[col].dtype in ['float64', 'float32']:
            # Round float values to 2 decimal places for display
            df[col] = df[col].round(2)
    
    return df

def get_data_summary(df: pd.DataFrame) -> dict:
    """Get a comprehensive summary of the DataFrame."""
    summary = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'duplicate_rows': df.duplicated().sum()
    }
    
    # Add numeric statistics
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
    
    # Add categorical statistics
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        categorical_summary = {}
        for col in categorical_cols:
            categorical_summary[col] = {
                'unique_values': df[col].nunique(),
                'most_common': df[col].mode().iloc[0] if not df[col].mode().empty else None
            }
        summary['categorical_summary'] = categorical_summary
    
    return summary

def export_dataframe(df: pd.DataFrame, filename: str, format: str = 'csv') -> bytes:
    """Export DataFrame to specified format."""
    if format.lower() == 'csv':
        return df.to_csv(index=False).encode('utf-8')
    elif format.lower() == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        return output.getvalue()
    else:
        raise ValueError(f"Unsupported export format: {format}")

def suggest_query_improvements(query: str) -> list:
    """Suggest improvements for SQL queries."""
    suggestions = []
    
    query_upper = query.upper()
    
    # Check for LIMIT clause
    if 'LIMIT' not in query_upper:
        suggestions.append("Consider adding a LIMIT clause to prevent large result sets")
    
    # Check for WHERE clause
    if 'WHERE' not in query_upper and 'SELECT *' in query_upper:
        suggestions.append("Consider adding a WHERE clause to filter results")
    
    # Check for ORDER BY
    if 'ORDER BY' not in query_upper and ('TOP' in query_upper or 'LIMIT' in query_upper):
        suggestions.append("Consider adding ORDER BY clause when using LIMIT or TOP")
    
    return suggestions
