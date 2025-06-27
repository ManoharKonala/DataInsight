import json
import os
from typing import Dict, Any
from openai import OpenAI

class NLToSQLConverter:
    """Converts natural language questions to SQL queries using OpenAI."""
    
    def __init__(self):
        """Initialize the converter with OpenAI client."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
    def convert_to_sql(self, question: str, table_name: str, table_schema: Dict[str, Any]) -> str:
        """Convert natural language question to SQL query."""
        try:
            # Prepare context about the table
            context = self._prepare_table_context(table_name, table_schema)
            
            # Create prompt for SQL generation
            prompt = self._create_sql_prompt(question, context)
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL developer. Generate accurate SQL queries based on natural language questions. Always return valid SQLite-compatible SQL queries. Return only the SQL query without any explanation or markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the SQL query
            sql_query = self._clean_sql_query(sql_query)
            
            return sql_query
            
        except Exception as e:
            raise Exception(f"Error converting natural language to SQL: {str(e)}")
    
    def get_query_suggestions(self, table_name: str, table_schema: Dict[str, Any]) -> list:
        """Generate suggested queries based on table schema."""
        try:
            context = self._prepare_table_context(table_name, table_schema)
            
            prompt = f"""
            Based on this table schema, suggest 5 useful analytical questions that a business analyst might ask:
            
            {context}
            
            Return the suggestions as a JSON array of strings. Each suggestion should be a natural language question.
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business intelligence expert. Generate practical analytical questions that would provide business insights. Return only a JSON array of question strings."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('suggestions', [])
            
        except Exception as e:
            # Return fallback suggestions if API fails
            return [
                f"What are the top 10 records in {table_name}?",
                f"Show me the summary statistics for {table_name}",
                f"What is the distribution of values in {table_name}?",
                f"Find any trends or patterns in {table_name}",
                f"What are the most common values in {table_name}?"
            ]
    
    def _prepare_table_context(self, table_name: str, table_schema: Dict[str, Any]) -> str:
        """Prepare context string describing the table structure."""
        context = f"Table name: {table_name}\n\n"
        context += "Columns:\n"
        
        for column in table_schema['columns']:
            context += f"- {column['name']} ({column['type']})"
            if column['primary_key']:
                context += " [PRIMARY KEY]"
            if column['not_null']:
                context += " [NOT NULL]"
            context += "\n"
        
        # Add sample data if available
        if 'sample_data' in table_schema and table_schema['sample_data']:
            context += "\nSample data (first few rows):\n"
            column_names = [col['name'] for col in table_schema['columns']]
            context += " | ".join(column_names) + "\n"
            context += "-" * (len(" | ".join(column_names))) + "\n"
            
            for row in table_schema['sample_data'][:3]:
                context += " | ".join(str(val) for val in row) + "\n"
        
        return context
    
    def _create_sql_prompt(self, question: str, table_context: str) -> str:
        """Create a detailed prompt for SQL generation."""
        prompt = f"""
        Convert this natural language question into a SQL query:
        
        Question: "{question}"
        
        Database context:
        {table_context}
        
        Requirements:
        1. Generate valid SQLite-compatible SQL
        2. Use appropriate WHERE clauses, JOINs, GROUP BY, ORDER BY as needed
        3. Include LIMIT clauses for large result sets (default to 100 if not specified)
        4. Handle null values appropriately
        5. Use proper column names and table names as provided
        6. For aggregation questions, use appropriate aggregate functions (COUNT, SUM, AVG, etc.)
        7. For "top N" questions, use ORDER BY with LIMIT
        8. For trend analysis, consider using date/time columns if available
        
        Return only the SQL query without any explanation or formatting.
        """
        
        return prompt
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean and validate the generated SQL query."""
        # Remove markdown formatting if present
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        # Remove any explanatory text before or after the query
        lines = sql_query.split('\n')
        sql_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('#'):
                sql_lines.append(line)
        
        sql_query = ' '.join(sql_lines)
        
        # Ensure query ends with semicolon
        if not sql_query.endswith(';'):
            sql_query += ';'
        
        return sql_query
    
    def explain_query(self, sql_query: str) -> str:
        """Provide a natural language explanation of a SQL query."""
        try:
            prompt = f"""
            Explain this SQL query in simple terms that a business analyst would understand:
            
            {sql_query}
            
            Provide a clear, concise explanation of what this query does and what results it will return.
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analyst who explains SQL queries in business terms. Be clear and concise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Unable to explain query: {str(e)}"
