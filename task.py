## Importing libraries and files
from crewai import Task

# FIX: Fixed imports and removed tools import as tools will be passed to agents
from agents import financial_analyst, verifier, investment_advisor, risk_assessor

# FIX: 1) Improved task description and expected output to guarantee better results
# 2) Added context to each task from the previous agent
verification = Task(
    description="Read the file at {file_path} and verify it is a legitimate financial document.",
    expected_output="The type of the document type (e.g., 10-K, Annual Report) and the name of the company to ehich the document belongs.",
    agent=verifier,
    async_execution=False
)

## Creating a task to help solve user's query
analyze_financial_document = Task(
    description="""
    1. Read the file at {file_path} using the FinancialDocumentTool.
    2. Extract key metrics: Revenue, Net Income, Debt, Cash Flow.
    3. Answer the user query: {query}.
    """,
    expected_output="A detailed financial summary with cited numbers from the text.",

    agent=financial_analyst,
    context=[verification],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis = Task(
    description="Based on the Analyst's findings, provide a Buy/Sell/Hold recommendation with justification.",
    expected_output="A professional investment memo supporting the recommendation.",
    agent=investment_advisor,
    context=[analyze_financial_document],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment = Task(
    description="Analyze the findings for specific risks (regulatory, market, financial).",
    expected_output="A bulleted list of the top 5 risks detected in the document.",
    agent=risk_assessor,
    context=[analyze_financial_document],
    async_execution=False,
)

    
