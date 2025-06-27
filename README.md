
# DataInsightPro

**DataInsightPro** is a powerful, user-friendly data analysis tool that transforms natural language questions into SQL queries, executes them on your uploaded data, and provides instant visualizations—all through a modern Streamlit web interface.

---

## 🚀 Features

- **Natural Language to SQL**: Ask questions in plain English and get accurate SQL queries using OpenAI GPT-4o.
- **SQL Editor**: Write and execute custom SQL queries directly.
- **Data Upload**: Upload CSV or Excel files for instant analysis.
- **Automatic Visualizations**: Get interactive charts and summaries for your query results.
- **Query History**: View, re-run, and manage your past queries.
- **Modular Design**: Clean separation of database, AI, visualization, and utility logic.

---

## 🖥️ Demo

1. **Upload your data** (CSV/Excel).
2. **Ask a question** (e.g., "Show me the top 5 products by sales").
3. **See the generated SQL, results, and visualizations**—all in one place!

---

## 📦 Project Structure

```
DataInsightPro/
  ├── app.py                # Main Streamlit app
  ├── database.py           # SQLite database manager
  ├── nl_to_sql.py          # Natural language to SQL (OpenAI integration)
  ├── query_history.py      # Query history management
  ├── visualizations.py     # Plotly-based visualizations
  ├── utils.py              # File processing, validation, helpers
  ├── sample_data.csv       # Example dataset
  ├── sample_sales_data.csv # Example sales dataset
  ├── pyproject.toml        # Python dependencies
  ├── test_app.py           # Tests
  └── ...                   # Other config/scripts
```

---

## ⚙️ Installation

### 1. **Clone the repository**
```bash
git clone https://github.com/ManoharKonala/DataInsight.git
cd DataInsightPro
```

### 2. **Install dependencies**
```bash
pip install -r requirements.txt
```
Or, if using `pyproject.toml`:
```bash
pip install -e .
```

### 3. **Set your OpenAI API key**
Obtain an API key from [OpenAI](https://platform.openai.com/).

**On Linux/Mac:**
```bash
export OPENAI_API_KEY=your_openai_api_key
```
**On Windows (cmd):**
```cmd
set OPENAI_API_KEY=your_openai_api_key
```
**On PowerShell:**
```powershell
$env:OPENAI_API_KEY="your_openai_api_key"
```

### 4. **Run the app**
```bash
streamlit run DataInsightPro/app.py
```
Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📝 Usage

- **Upload Data**: Use the sidebar to upload a CSV or Excel file.
- **Ask Questions**: Use the "Natural Language Query" tab to ask questions in plain English.
- **SQL Editor**: Write and run your own SQL queries in the "SQL Editor" tab.
- **Visualizations**: Explore auto-generated charts in the "Visualizations" tab.
- **Query History**: Review and re-run previous queries in the "Query History" tab.

---

## 🛠️ Dependencies

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Plotly](https://plotly.com/python/)
- [Openpyxl](https://openpyxl.readthedocs.io/)

All dependencies are listed in `pyproject.toml`.

---

## 🔒 API & Security

- Requires an **OpenAI API key** for natural language to SQL conversion.
- Your data is processed locally and not sent to any third-party except for the NL-to-SQL conversion.

---

## 🧩 Architecture

- **Frontend**: Streamlit web UI
- **Backend**: Python modules for database, AI, and visualization
- **Database**: In-memory SQLite (fast, no external DB needed)
- **AI**: OpenAI GPT-4o for NL-to-SQL
- **Visualization**: Plotly for interactive charts

---

## 📚 Example Questions

- "What are the top 10 highest values?"
- "Show me the average by category"
- "What's the trend over time?"
- "Find outliers in the data"
- "Compare different groups"

---

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- OpenAI for GPT-4o
- Streamlit for the web framework
- Plotly for visualizations
- Pandas for data wrangling

---

## 💡 Tips

- Be specific in your questions and mention column names when possible.
- Use the SQL editor for advanced queries.
- Data is stored in-memory; upload your data each session.
