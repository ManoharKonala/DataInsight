# SQL Data Analysis Tool

## Overview

This is a Streamlit-based web application that transforms natural language questions into SQL queries and provides data analysis capabilities. The tool allows users to upload CSV/Excel files, ask questions in plain English, and get both SQL queries and visualizations as results.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit web interface for user interaction
- **Backend**: Python-based processing with modular components
- **Database**: SQLite in-memory database for data storage
- **AI Integration**: OpenAI GPT-4o for natural language to SQL conversion
- **Visualization**: Plotly for interactive charts and graphs

## Key Components

### Core Modules

1. **app.py**: Main Streamlit application entry point
   - Handles user interface and navigation
   - Manages session state across user interactions
   - Coordinates between different modules

2. **database.py**: DatabaseManager class
   - Manages SQLite database operations
   - Handles table creation from DataFrames
   - Executes SQL queries and returns results
   - Uses in-memory SQLite database by default for speed

3. **nl_to_sql.py**: NLToSQLConverter class
   - Converts natural language to SQL using OpenAI GPT-4o
   - Handles API communication with OpenAI
   - Includes prompt engineering for accurate SQL generation
   - Implements query validation and cleanup

4. **query_history.py**: QueryHistoryManager class
   - Tracks user queries and results
   - Stores history in JSON format
   - Provides search functionality across past queries
   - Limits history to last 100 queries for performance

5. **visualizations.py**: Visualization engine
   - Creates appropriate charts based on data types
   - Uses Plotly for interactive visualizations
   - Provides multiple view types (summary, charts, distribution, details)
   - Handles numeric, categorical, and datetime data types

6. **utils.py**: Utility functions
   - File processing for CSV/Excel uploads
   - Data cleaning and validation
   - SQL query validation
   - Table name generation and sanitization

### Configuration Files

- **.replit**: Replit environment configuration with Python 3.11
- **pyproject.toml**: Project dependencies and metadata
- **.streamlit/config.toml**: Streamlit server configuration

## Data Flow

1. **Data Upload**: User uploads CSV/Excel file through Streamlit interface
2. **Data Processing**: File is processed and loaded into pandas DataFrame
3. **Database Storage**: DataFrame is converted to SQLite table in memory
4. **Question Input**: User enters natural language question
5. **SQL Generation**: OpenAI GPT-4o converts question to SQL query
6. **Query Execution**: SQL query is executed against the database
7. **Result Processing**: Results are formatted and visualized
8. **History Storage**: Query and results are saved to history

## External Dependencies

### Required APIs
- **OpenAI API**: Requires OPENAI_API_KEY environment variable for GPT-4o access

### Python Packages
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **sqlite3**: Database operations (built-in)
- **openai**: OpenAI API client
- **plotly**: Interactive visualizations
- **openpyxl**: Excel file support

## Deployment Strategy

- **Platform**: Replit with autoscale deployment target
- **Runtime**: Python 3.11 with Nix package management
- **Server**: Streamlit server on port 5000
- **Database**: In-memory SQLite (data persists only during session)
- **Environment**: Requires OPENAI_API_KEY to be set in environment variables

### Scaling Considerations
- Uses in-memory database for fast access but limited to single session
- Query history stored in local JSON file
- Stateless design allows for horizontal scaling with external database

## Changelog

```
Changelog:
- June 20, 2025. Initial setup
- June 20, 2025. Fixed server startup issues and configured port 5000 for deployment
- June 20, 2025. Added sample sales dataset for testing natural language queries
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

### Architecture Decisions

**Database Choice**: SQLite in-memory database was chosen for simplicity and speed. This provides fast query execution without external dependencies, though data doesn't persist between sessions.

**AI Model**: GPT-4o was selected as the most capable model for natural language to SQL conversion, providing high accuracy for complex queries.

**Visualization Library**: Plotly was chosen over matplotlib for its interactive capabilities and better integration with Streamlit.

**File Storage**: Local JSON file for query history keeps the application simple while providing basic persistence during sessions.

**Modular Design**: Each component is separated into its own module to improve maintainability and allow for easy testing and updates.