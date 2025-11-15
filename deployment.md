Install dependencies
pip install -r requirements.txt

Run demo pipeline
python core.py

3. Optional: Deploy as an API

Wrap pipeline() inside FastAPI or Flask endpoint.

Add POST /qualify_leads route.

Send JSON containing a list of leads.

4. Optional: Integrate real ADK tools

Replace llm_reasoning_prompt() with ADK LLM tool (e.g., Gemini).

Replace CompanyEnricherTool() with Search/Enrichment ADK tools.
