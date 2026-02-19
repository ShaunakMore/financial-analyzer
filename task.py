## Importing libraries and files
from crewai import Task

# FIX: Fixed imports and removed tools import as tools will be passed to agents
from agents import financial_analyst, verifier, investment_advisor, risk_assessor

# FIX: 1) Improved task description and expected output to guarantee better results
# 2) Added context to each task from the previous agent
verification = Task(
    description=(
        """
        Verify that the file at {file_path} is a valid financial document.
        Use your tool to read the file and examine its contents.
        Check for the presence of financial data such as income statements, balance sheets, cash flow statements, or other standard financial reporting structures.
        If the file does not appear to be a financial document, clearly state this and stop.
        Do not fabricate financial content or approve non-financial documents as financial reports.
        """
    ),
    expected_output=(
        """
        A verification report containing:
        1. Confirmation of whether the file is a valid financial document (Yes / No / Partially)
        2. Summary of the financial content types identified (e.g., balance sheet, income statement)
        
        """
    ),
    agent=verifier,
    async_execution=False
)

## Creating a task to help solve user's query
analyze_financial_document = Task(
    description=("""
        Analyze the financial document provided by the user to answer their query: {query}
        Use your tools to read the document at path {file_path} and extract key financial metrics, performance indicators, and relevant data points
        Identify notable trends, strengths, and concerns present in the document.
        Search the internet only if additional market context is needed to supplement the document analysis.
        Base all findings strictly on data from the document — do not fabricate figures or sources.
        """
    ),
    expected_output=(
        """
        A structured financial analysis report containing:
        1. A summary of the document's key financial data (revenue, profit, debt, etc.)
        2. Notable trends or year-over-year changes identified in the document
        3. Strengths and areas of concern based on the financials
        4. A direct answer to the user's query: {query}
        5. Citations referencing specific sections or figures from the document
        """
    ),
    agent=financial_analyst,
    context=[verification],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis = Task(
    description=(
        """
        Using the financial analysis report provided in your context, provide investment considerations relevant to: {query}
        Use your tool to process the financial data from the report and extract investment signals.
        Analyze key financial ratios (P/E, debt-to-equity, ROE, etc.) identified in the report.
        Evaluate the company's financial health and growth trajectory based on the analyst's findings.
        Provide balanced investment considerations — including both potential opportunities and risks.
        Do not recommend specific investment products. Remind users to consult a licensed financial advisor.
        """
    ),
    expected_output=(
        """
        A balanced investment considerations report containing:
        1. Key financial ratios from the analyst's report and their investment significance
        2. Assessment of the company's financial position and growth indicators
        3. Potential investment opportunities supported by the analyst's findings
        4. Key risks and concerns an investor should be aware of
        5. A disclaimer advising users to seek professional financial advice before making decisions
        """
    ),
    agent=investment_advisor,
    context=[analyze_financial_document],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment = Task(
    description=(
        """
        Using the financial analysis report provided in your context, perform a thorough risk assessment in the context of: {query}
        Use your tool to scan the analyst's report and identify risk signals across categories: liquidity, market, credit, operational, and strategic risk.
        Use data from the report to substantiate each identified risk.
        Suggest evidence-based risk mitigation strategies appropriate to the company's financial profile.
        Avoid overstating or dramatizing risks — provide an objective, grounded assessment.
        """
    ),
    expected_output=(
        """
        A professional risk assessment report containing
        1. Identified risk categories with supporting evidence from the analyst's report
        2. Severity rating for each risk (Low / Medium / High) with justification
        3. Recommended risk mitigation strategies grounded in the financials
        4. Overall risk profile summary for the entity described in the document
        """
    ),
    agent=risk_assessor,
    context=[analyze_financial_document],
    async_execution=False,
)

    
