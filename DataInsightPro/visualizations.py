import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Any, List, Dict

def create_visualizations(df: pd.DataFrame, context: str = "") -> None:
    """Create appropriate visualizations based on the DataFrame content."""
    
    if df.empty:
        st.warning("No data available for visualization.")
        return
    
    # Get numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # Convert string columns that might be dates
    for col in categorical_cols:
        if df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col])
                datetime_cols.append(col)
                categorical_cols.remove(col)
            except:
                pass
    
    # Create tabs for different visualization types
    if len(numeric_cols) > 0 or len(categorical_cols) > 0:
        viz_tabs = st.tabs(["📊 Summary", "📈 Charts", "🔍 Distribution", "📋 Details"])
        
        with viz_tabs[0]:
            _create_summary_visualizations(df, numeric_cols, categorical_cols)
        
        with viz_tabs[1]:
            _create_chart_visualizations(df, numeric_cols, categorical_cols, datetime_cols, context)
        
        with viz_tabs[2]:
            _create_distribution_visualizations(df, numeric_cols, categorical_cols)
        
        with viz_tabs[3]:
            _create_detailed_analysis(df, numeric_cols, categorical_cols)
    else:
        st.info("No suitable columns found for visualization.")

def _create_summary_visualizations(df: pd.DataFrame, numeric_cols: List[str], categorical_cols: List[str]) -> None:
    """Create summary visualizations."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Data Summary")
        st.write(f"**Rows:** {len(df)}")
        st.write(f"**Columns:** {len(df.columns)}")
        st.write(f"**Numeric columns:** {len(numeric_cols)}")
        st.write(f"**Categorical columns:** {len(categorical_cols)}")
        
        # Missing values
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            st.write("**Missing values:**")
            for col, missing in missing_data.items():
                if missing > 0:
                    st.write(f"- {col}: {missing} ({missing/len(df)*100:.1f}%)")
        else:
            st.write("**No missing values** ✅")
    
    with col2:
        if len(numeric_cols) > 0:
            st.subheader("🔢 Numeric Summary")
            st.dataframe(df[numeric_cols].describe())

def _create_chart_visualizations(df: pd.DataFrame, numeric_cols: List[str], 
                                categorical_cols: List[str], datetime_cols: List[str], 
                                context: str) -> None:
    """Create various chart visualizations."""
    
    # Auto-suggest best visualizations based on data
    suggested_charts = _suggest_charts(df, numeric_cols, categorical_cols, datetime_cols, context)
    
    if suggested_charts:
        st.subheader("🎯 Suggested Visualizations")
        
        for i, chart_info in enumerate(suggested_charts):
            st.write(f"**{chart_info['title']}**")
            try:
                chart_info['function'](df, chart_info['params'])
            except Exception as e:
                st.error(f"Error creating chart: {str(e)}")
            
            if i < len(suggested_charts) - 1:
                st.markdown("---")
    
    # Interactive chart builder
    st.subheader("🛠️ Custom Chart Builder")
    
    chart_type = st.selectbox(
        "Select chart type:",
        ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Histogram", "Pie Chart"]
    )
    
    if chart_type == "Bar Chart" and (len(categorical_cols) > 0 and len(numeric_cols) > 0):
        x_col = st.selectbox("X-axis (categorical):", categorical_cols)
        y_col = st.selectbox("Y-axis (numeric):", numeric_cols)
        if st.button("Create Bar Chart"):
            _create_bar_chart(df, {'x': x_col, 'y': y_col})
    
    elif chart_type == "Line Chart" and len(numeric_cols) >= 2:
        x_col = st.selectbox("X-axis:", df.columns.tolist())
        y_col = st.selectbox("Y-axis:", numeric_cols)
        if st.button("Create Line Chart"):
            _create_line_chart(df, {'x': x_col, 'y': y_col})
    
    elif chart_type == "Scatter Plot" and len(numeric_cols) >= 2:
        x_col = st.selectbox("X-axis:", numeric_cols)
        y_col = st.selectbox("Y-axis:", [col for col in numeric_cols if col != x_col])
        color_col = st.selectbox("Color by (optional):", ["None"] + categorical_cols)
        if st.button("Create Scatter Plot"):
            params = {'x': x_col, 'y': y_col}
            if color_col != "None":
                params['color'] = color_col
            _create_scatter_plot(df, params)

def _create_distribution_visualizations(df: pd.DataFrame, numeric_cols: List[str], categorical_cols: List[str]) -> None:
    """Create distribution visualizations."""
    
    if len(numeric_cols) > 0:
        st.subheader("📈 Numeric Distributions")
        
        # Histograms for numeric columns
        for col in numeric_cols[:4]:  # Limit to first 4 numeric columns
            fig = px.histogram(df, x=col, title=f"Distribution of {col}")
            st.plotly_chart(fig, use_container_width=True)
    
    if len(categorical_cols) > 0:
        st.subheader("📊 Categorical Distributions")
        
        # Bar charts for categorical columns
        for col in categorical_cols[:4]:  # Limit to first 4 categorical columns
            value_counts = df[col].value_counts().head(10)  # Top 10 values
            
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"Distribution of {col}",
                labels={'x': col, 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)

def _create_detailed_analysis(df: pd.DataFrame, numeric_cols: List[str], categorical_cols: List[str]) -> None:
    """Create detailed analysis views."""
    
    st.subheader("🔍 Detailed Analysis")
    
    # Correlation matrix for numeric columns
    if len(numeric_cols) > 1:
        st.write("**Correlation Matrix**")
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            title="Correlation Matrix",
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Value counts for categorical columns
    if len(categorical_cols) > 0:
        st.write("**Categorical Value Counts**")
        selected_cat_col = st.selectbox("Select categorical column:", categorical_cols)
        
        if selected_cat_col:
            value_counts = df[selected_cat_col].value_counts()
            st.dataframe(value_counts.head(20))
    
    # Data quality insights
    st.write("**Data Quality Insights**")
    
    quality_issues = []
    
    # Check for duplicates
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        quality_issues.append(f"Found {duplicate_count} duplicate rows")
    
    # Check for potential outliers in numeric columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
        if len(outliers) > 0:
            quality_issues.append(f"Column '{col}' has {len(outliers)} potential outliers")
    
    if quality_issues:
        for issue in quality_issues:
            st.warning(issue)
    else:
        st.success("No obvious data quality issues detected!")

def _suggest_charts(df: pd.DataFrame, numeric_cols: List[str], categorical_cols: List[str], 
                   datetime_cols: List[str], context: str) -> List[Dict[str, Any]]:
    """Suggest appropriate charts based on data characteristics."""
    
    suggestions = []
    
    # Time series chart if datetime column exists
    if len(datetime_cols) > 0 and len(numeric_cols) > 0:
        suggestions.append({
            'title': 'Time Series Trend',
            'function': _create_line_chart,
            'params': {'x': datetime_cols[0], 'y': numeric_cols[0]}
        })
    
    # Bar chart for categorical vs numeric
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        suggestions.append({
            'title': 'Category Analysis',
            'function': _create_bar_chart,
            'params': {'x': categorical_cols[0], 'y': numeric_cols[0]}
        })
    
    # Scatter plot for numeric relationships
    if len(numeric_cols) >= 2:
        suggestions.append({
            'title': 'Relationship Analysis',
            'function': _create_scatter_plot,
            'params': {'x': numeric_cols[0], 'y': numeric_cols[1]}
        })
    
    # Distribution chart
    if len(numeric_cols) > 0:
        suggestions.append({
            'title': 'Distribution Analysis',
            'function': _create_histogram,
            'params': {'x': numeric_cols[0]}
        })
    
    return suggestions[:3]  # Return top 3 suggestions

def _create_bar_chart(df: pd.DataFrame, params: Dict[str, str]) -> None:
    """Create a bar chart."""
    x_col, y_col = params['x'], params['y']
    
    # Aggregate data if needed
    if df[x_col].dtype == 'object':
        chart_data = df.groupby(x_col)[y_col].agg(['mean', 'sum', 'count']).reset_index()
        
        # Choose appropriate aggregation
        if 'sum' in params.get('agg', 'mean'):
            y_values = chart_data['sum']
            title = f"Sum of {y_col} by {x_col}"
        else:
            y_values = chart_data['mean']
            title = f"Average {y_col} by {x_col}"
        
        fig = px.bar(
            x=chart_data[x_col],
            y=y_values,
            title=title,
            labels={'x': x_col, 'y': y_col}
        )
    else:
        fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
    
    st.plotly_chart(fig, use_container_width=True)

def _create_line_chart(df: pd.DataFrame, params: Dict[str, str]) -> None:
    """Create a line chart."""
    x_col, y_col = params['x'], params['y']
    
    fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
    st.plotly_chart(fig, use_container_width=True)

def _create_scatter_plot(df: pd.DataFrame, params: Dict[str, str]) -> None:
    """Create a scatter plot."""
    x_col, y_col = params['x'], params['y']
    color_col = params.get('color')
    
    if color_col:
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, 
                        title=f"{y_col} vs {x_col} (colored by {color_col})")
    else:
        fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
    
    st.plotly_chart(fig, use_container_width=True)

def _create_histogram(df: pd.DataFrame, params: Dict[str, str]) -> None:
    """Create a histogram."""
    x_col = params['x']
    
    fig = px.histogram(df, x=x_col, title=f"Distribution of {x_col}")
    st.plotly_chart(fig, use_container_width=True)
