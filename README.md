# 📊 Financial Document Analyzer

A multi-agent AI system built with **CrewAI** and **FastAPI** that analyzes financial PDF documents to provide investment insights, risk assessments, and compliance verification.

---

## 🐛 Bugs Found & Fixes Applied

### `agents.py`

**Bug 1 — Wrong import path for `Agent`**
- ❌ `from crewai.agents import Agent`
- ✅ `from crewai import Agent, LLM`

**Bug 2 — Missing imports for `tools`**
- ✅ `from tools import search_tool, FinancialDocumentTool, RiskTool, InvestmentTool`

**Bug 3 — llm variable not instantiated as a CrewAI `LLM` object**
- The llm was not using CrewAI's native `LLM` class, which is required for proper integration.
- ✅ Fixed by defining `llm` using `LLM(model=..., temperature=..., api_key=..., config=...)`.

**Bug 4 — All agents had the same tool (`FinancialDocumentTool`) regardless of role**
- Assigning irrelevant tools to agents caused confusion and degraded output quality.
- ✅ Fixed by assigning role-appropriate tools:
  - `financial_analyst` → `FinancialDocumentTool`, `search_tool`
  - `verifier` → `FinancialDocumentTool`
  - `investment_advisor` → `InvestmentTool`
  - `risk_assessor` → `RiskTool`

**Bug 5 — Agent roles and goals were too generic**
- Vague goals produced inconsistent LLM outputs.
- ✅ Improved all agent `role`, `goal`, and `backstory` fields for precision and reliability.

**Bug 6 — `max_iter` too low causing premature tool exits**
- ✅ Set `max_iter=2` on all agents to allow for retries on invalid tool calls.

---

### `tools.py`

**Bug 7 — Wrong import for `SerperDevTool`**
- ❌ `from crewai_tools.tools import SerperDevTool`
- ✅ `from crewai_tools import SerperDevTool`

**Bug 8 — `FinancialDocumentTool`, `InvestmentTool`, and `RiskTool` did not inherit from `BaseTool`**
- Custom tools must extend `BaseTool` to be compatible with CrewAI agents.
- ✅ All three tools now properly inherit from `crewai.tools.BaseTool`.

**Bug 9 — `_run` and `_arun` methods were missing from all custom tools**
- Without these methods, tools raised `NotImplementedError` at runtime.
- ✅ Both `_run` (sync) and `_arun` (async wrapper) implemented for all tools.

**Bug 10 — Missing import for `PyPDFLoader`**
- ❌ `PyPDFLoader` was used but never imported.
- ✅ Fixed: `from langchain_community.document_loaders import PyPDFLoader as Pdf`

**Bug 11 —  Pydantic input schemas missing**
- Tools had no `args_schema` defined, meaning CrewAI had no way to validate or structure the inputs passed to them at runtime.
- ✅ Fixed by adding Pydantic models with properly typed and described fields, then linking them via `args_schema` on each tool.

---

### `main.py`

**Bug 12 — API endpoint function named `analyze_financial_document` conflicted with the task function name**
- This caused import shadowing and routing ambiguity.
- ✅ Renamed the endpoint to `analyze_financial_endpoint`.

**Bug 13 — `Crew` was not properly defined**
- Missing explicit `agents`, `tasks`, and `process` arguments.
- ✅ `run_crew()` now properly instantiates `Crew` with all required parameters using `Process.sequential`.

---

### `task.py`

**Bug 14 — Tasks imported tools directly instead of relying on agents**
- Tools are attached to agents, not tasks. Importing tools into `task.py` caused redundancy and potential conflicts.
- ✅ Removed all tool imports from `task.py`; tools are resolved through agents.

**Bug 15 — No `context` chaining between tasks**
- Tasks had no awareness of each other's outputs, resulting in disconnected analysis.
- ✅ Added `context=[...]` to downstream tasks so each agent builds on previous findings.

**Bug 16 — Weak `description` and `expected_output` strings**
- Vague task descriptions produced inconsistent, low-quality LLM outputs.
- ✅ Rewrote all task descriptions to be explicit and structured, with clear `expected_output` definitions.

**Bug 17 — Same `agent` parameter for all tasks**
- All tasks were passed the same `financeagent` agent
- ✅ Assigned proper values to `agent` param.

---

## ⚙️ Setup & Usage Instructions

### Prerequisites

- Python 3.10+
- A [Gemini API Key](https://aistudio.google.com/) (stored in `.env`)
- A [Serper API Key](https://serper.dev/) for web search (stored in `.env`)

### Installation

```bash
# Clone the repository
git clone https://github.com/ShaunakMore/financial-analyzer.git
cd financial-analyzer
```
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

or

```bash
# Create and activate a virtual environment using uv (Recommended)
uv sync

```


### Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

### Running the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

## 📡 API Documentation

### Base URL

```
http://localhost:8000
```

---

### `GET /`

**Health Check** — Confirms the API is running.

**Response**
```json
{
  "message": "Financial Document Analyzer API is running"
}
```

---

### `POST /analyze`

**Analyze a Financial Document** — Uploads a PDF and runs the full multi-agent analysis pipeline.

#### Request

| Type | Field | Required | Description |
|------|-------|----------|-------------|
| `multipart/form-data` | `file` | ✅ Yes | PDF financial document to analyze |
| `multipart/form-data` | `query` | ❌ No | Custom question or focus area (defaults to general investment analysis) |

#### Example (curl)

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@apple_10k.pdf" \
  -F "query=What is the revenue growth trend and should I buy this stock?"
```

#### Example (Python)

```python
import requests

with open("apple_10k.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"file": f},
        data={"query": "Summarize the key financial risks in this report."}
    )

print(response.json())
```

#### Success Response (`200 OK`)

```json
{
  "status": "success",
  "query": "Summarize the key financial risks in this report.",
  "analysis": "\nANALYSIS:\n...\n\nINVESTMENT INSIGHT:\n...\n\nRISK ANALYSIS:\n...",
  "file_processed": "data/apple_10k.pdf_<uuid>.pdf"
}
```

#### Error Response (`500 Internal Server Error`)

```json
{
  "detail": "Error processing financial document: <error message>"
}
```

---

## 🤖 Agent Pipeline Overview

The system runs four agents sequentially, each building on the previous:

| Step | Agent | Role | Output |
|------|-------|------|--------|
| 1 | **Verifier** | Document Compliance Officer | Confirms document type and company name |
| 2 | **Financial Analyst** | Senior Financial Analyst | Extracts revenue, income, debt, cash flow; answers user query |
| 3 | **Investment Advisor** | Investment Strategist | Provides Buy/Sell/Hold recommendation memo |
| 4 | **Risk Assessor** | Chief Risk Officer | Lists top 5 risks detected in the document |

> **Note:** The `FinancialDocumentTool` applies a 5,000-character cap on PDF content due to free-tier API token limits. Remove this cap in production for full document analysis.