import streamlit as st
import pandas as pd
import sqlite3
import os
from database import DatabaseManager
from nl_to_sql import NLToSQLConverter
from query_history import QueryHistoryManager
from visualizations import create_visualizations
from utils import process_uploaded_file, validate_sql_query

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'nl_converter' not in st.session_state:
    st.session_state.nl_converter = NLToSQLConverter()
if 'query_history' not in st.session_state:
    st.session_state.query_history = QueryHistoryManager()
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'current_table' not in st.session_state:
    st.session_state.current_table = None

st.set_page_config(
    page_title="SQL Data Analysis Tool",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Natural Language to SQL Data Analysis Tool")
st.markdown("Transform your questions into insights with AI-powered SQL generation")

# Sidebar for navigation and data management
with st.sidebar:
    st.header("Data Management")
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your data file to start analyzing"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing file..."):
                df, table_name = process_uploaded_file(uploaded_file)
                st.session_state.db_manager.create_table_from_dataframe(df, table_name)
                st.session_state.current_data = df
                st.session_state.current_table = table_name
                st.success(f"✅ File uploaded successfully! Table: `{table_name}`")
                
                # Show data preview
                with st.expander("Data Preview"):
                    st.dataframe(df.head(10))
                    st.info(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    # Available tables
    st.header("Available Tables")
    tables = st.session_state.db_manager.get_table_names()
    if tables:
        selected_table = st.selectbox("Select table:", tables)
        if selected_table:
            st.session_state.current_table = selected_table
            # Show table info
            columns = st.session_state.db_manager.get_table_columns(selected_table)
            with st.expander(f"Table Info: {selected_table}"):
                st.write("**Columns:**")
                for col in columns:
                    st.write(f"- {col}")
    else:
        st.info("No tables available. Upload a file to get started.")

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["💬 Natural Language Query", "📝 SQL Editor", "📈 Visualizations", "📚 Query History"])

with tab1:
    st.header("Ask Questions About Your Data")
    
    if st.session_state.current_table:
        # Example questions
        st.subheader("Example Questions:")
        example_questions = [
            "What are the top 10 highest values?",
            "Show me the average by category",
            "What's the trend over time?",
            "Find outliers in the data",
            "Compare different groups"
        ]
        
        cols = st.columns(len(example_questions))
        for i, question in enumerate(example_questions):
            if cols[i].button(question, key=f"example_{i}"):
                st.session_state.user_question = question
        
        # Natural language input
        user_question = st.text_area(
            "Enter your question:",
            value=st.session_state.get('user_question', ''),
            height=100,
            placeholder="e.g., 'Show me the top 5 customers by revenue this year'"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            analyze_button = st.button("🔍 Analyze", type="primary")
        
        if analyze_button and user_question:
            try:
                with st.spinner("Converting your question to SQL..."):
                    # Get table schema for context
                    table_schema = st.session_state.db_manager.get_table_schema(st.session_state.current_table)
                    
                    # Convert natural language to SQL
                    sql_query = st.session_state.nl_converter.convert_to_sql(
                        user_question, 
                        st.session_state.current_table, 
                        table_schema
                    )
                    
                    st.subheader("Generated SQL Query:")
                    st.code(sql_query, language='sql')
                    
                    # Execute query
                    with st.spinner("Executing query..."):
                        result_df = st.session_state.db_manager.execute_query(sql_query)
                        
                        if not result_df.empty:
                            st.subheader("Query Results:")
                            st.dataframe(result_df, use_container_width=True)
                            
                            # Save to history
                            st.session_state.query_history.add_query(
                                user_question, sql_query, len(result_df)
                            )
                            
                            # Auto-generate visualizations
                            st.subheader("Visualizations:")
                            create_visualizations(result_df, user_question)
                            
                        else:
                            st.warning("Query returned no results.")
                            
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Try rephrasing your question or check if the table contains the requested data.")
    else:
        st.info("👆 Please upload a data file or select a table from the sidebar to start asking questions.")

with tab2:
    st.header("SQL Query Editor")
    
    if st.session_state.current_table:
        # SQL editor
        sql_query = st.text_area(
            "Enter SQL query:",
            height=200,
            placeholder=f"SELECT * FROM {st.session_state.current_table} LIMIT 10;",
            help="Write your SQL query here. Use the table name from the sidebar."
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            execute_button = st.button("▶️ Execute", type="primary")
        
        if execute_button and sql_query:
            try:
                # Validate query
                if validate_sql_query(sql_query):
                    with st.spinner("Executing query..."):
                        result_df = st.session_state.db_manager.execute_query(sql_query)
                        
                        if not result_df.empty:
                            st.subheader("Query Results:")
                            st.dataframe(result_df, use_container_width=True)
                            
                            # Save to history
                            st.session_state.query_history.add_query(
                                "Manual SQL Query", sql_query, len(result_df)
                            )
                            
                            # Option to visualize
                            if st.button("📊 Create Visualizations"):
                                create_visualizations(result_df, "SQL Query Results")
                        else:
                            st.warning("Query returned no results.")
                else:
                    st.error("Invalid SQL query. Please check your syntax.")
            except Exception as e:
                st.error(f"Error executing query: {str(e)}")
    else:
        st.info("👆 Please select a table from the sidebar to start writing SQL queries.")

with tab3:
    st.header("Data Visualizations")
    
    if st.session_state.current_table and st.session_state.current_data is not None:
        st.subheader("Quick Data Overview")
        
        # Basic statistics
        numeric_cols = st.session_state.current_data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.write("**Numeric Columns Summary:**")
            st.dataframe(st.session_state.current_data[numeric_cols].describe())
        
        # Create visualizations for the current data
        create_visualizations(st.session_state.current_data, "Data Overview")
        
    else:
        st.info("👆 Upload data to see visualizations here.")

with tab4:
    st.header("Query History")
    
    history = st.session_state.query_history.get_history()
    
    if history:
        st.subheader("Recent Queries")
        
        for i, query_info in enumerate(reversed(history[-10:])):  # Show last 10 queries
            with st.expander(f"Query {len(history)-i}: {query_info['question'][:50]}..."):
                st.write("**Question:**", query_info['question'])
                st.code(query_info['sql_query'], language='sql')
                st.write(f"**Results:** {query_info['result_count']} rows")
                st.write(f"**Timestamp:** {query_info['timestamp']}")
                
                # Re-run query button
                if st.button(f"🔄 Re-run Query", key=f"rerun_{i}"):
                    try:
                        result_df = st.session_state.db_manager.execute_query(query_info['sql_query'])
                        st.dataframe(result_df)
                    except Exception as e:
                        st.error(f"Error re-running query: {str(e)}")
        
        # Clear history button
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.query_history.clear_history()
            st.success("Query history cleared!")
            st.rerun()
    else:
        st.info("No queries in history yet. Start by asking questions about your data!")

# Footer
st.markdown("---")
st.markdown("💡 **Tips:** Be specific in your questions, mention column names when possible, and use natural language as you would when talking to a data analyst.")
