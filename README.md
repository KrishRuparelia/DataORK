
# DataOrk

DataOrk lets you ask questions about PostgreSQL data and request API/file ETL
tasks in natural language. The app routes requests to the SQL or ETL agent.

## Run the UI

1. Install dependencies with `uv sync`.
2. Copy `.env.example` to `.env` and fill in your OpenAI API key. Add PostgreSQL
   values if you want to use the SQL analyst.
3. Start the app:

   ```powershell
   uv run streamlit run app.py
   ```

The UI runs locally. Keep `.env` private; it is excluded from Git.
