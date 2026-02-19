## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# FIX: Import fixed crewai.agents -> crewai
from crewai import Agent,LLM

# FIX: Imports fixed
from tools import search_tool, FinancialDocumentTool, RiskTool, InvestmentTool

### Loading LLM
# FIX: Defined llm AS CrewAI integration using LLM class
llm = LLM(
    model="gemini/gemma-3-27b-it", # Better rate-limits with gemma on free tier
    temperature=0.1,
    api_key=os.getenv("GEMINI_API_KEY"),
    config={"timeout": 3000}, # Increased timeout due to gemini api timeout errors
)

# Creating an Experienced Financial Analyst agent
# FIX: 1) Optimised roles and goals for all the agents for best result, 
# 2) Increased max_iters to account for any invalid calls
# 3) Added tools to agents based on their respective roles instead of just the FinancialDocumentTool() to all
financial_analyst=Agent(
    role="Senior Financial Analyst",
    goal="Accurately analyze financial documents to extract facts. Query: {query}",
    verbose=True,
    backstory=(
        "You are an experienced analyst at a top-tier investment bank."
        "You rely strictly on the data provided in documents."
        "You never make up numbers. If data is missing, you state that it is missing."
    ),
    tools=[FinancialDocumentTool(), search_tool],
    llm=llm,
    max_iter=1,  
)

# Creating a document verifier agent
verifier = Agent(
    role="Document Compliance Officer",
    goal="Verify if the uploaded file is a valid financial document.",
    verbose=True,
    backstory=(
        "You are a diligent compliance officer."
        "You quickly identify if a document is a valid financial report or irrelevant noise."
    ),
    llm=llm,
    tools=[FinancialDocumentTool()],
    max_iter=1,
)


investment_advisor = Agent(
    role="Investment Strategist",
    goal="Provide sound investment recommendations based on verified financial data.",
    verbose=True,
    backstory=(
        "You are a fiduciary investment advisor."
        "You prioritize long-term value and risk management."
        "You base your advice solely on the Analyst's findings."
    ),
    llm=llm,
    tools=[InvestmentTool()],
    max_iter=1,
)


risk_assessor = Agent(
    role="Chief Risk Officer",
    goal="Identify potential market and operational risks.",
    verbose=True,
    backstory=(
        "You are responsible for protecting capital."
        "You look for red flags like high debt or declining margins."
    ),
    llm=llm,
    max_iter=1,
    tools=[RiskTool()],
)
