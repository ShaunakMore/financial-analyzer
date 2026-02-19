## Importing libraries and files
import os
import re
from dotenv import load_dotenv
load_dotenv()

# FIX: Import fixed for SerperDevTool
from crewai_tools import SerperDevTool
from crewai.tools import BaseTool
from pydantic import BaseModel,Field

# FIX: Added missing import for Pdf
from langchain_community.document_loaders import PyPDFLoader as Pdf

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
# FIX: FinanceDocumentTool inherits from BaseTool class

class FinancialDocumentInput(BaseModel):
    file_path: str = Field(..., description="The path to the PDF file to read.")

class FinancialDocumentTool(BaseTool):
    name: str = "Financial Document Reader"
    description: str = "Reads a financial PDF document. You MUST provide the 'file_path'."
    args_schema: type[BaseModel] = FinancialDocumentInput
    # FIX: Added the _run and _arun method
    
    def _run(self,file_path):
        """Tool to read data from a pdf file from a path

        Args:
            path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full Financial Document file
        """
        
        docs = Pdf(file_path=file_path).load()

        full_report = ""
        for data in docs:
            # Clean and format the financial document data
            content = data.page_content
            
            # Remove extra whitespaces and format properly
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")
                
            full_report += content + "\n"
        
        # NOTE: A limit of 5000 words added due to free-tier api token and rate limit limitation.
        # This is to be removed in production.    
        return full_report[:5000]
    
    async def _arun(self, file_path) -> str:
        return self._run(file_path)
    

## Creating Investment Analysis Tool
# FIX: InvestmentTool now inherits from BaseTool


class InvestmentInput(BaseModel):
    financial_data: str = Field(..., description="The text content of the financial report.")

class InvestmentTool(BaseTool):
    name: str = "Investment Analysis Tool"
    description: str = "Analyzes raw financial text to extract money figures and percentages."
    args_schema: type[BaseModel] = InvestmentInput 
    
    def _run(self, financial_data: str):
        """
        Parses financial text to find potential money figures and percentages
        that are relevant for investment analysis.
        """
        # 1. Clean the text
        clean_text = " ".join(financial_data.split())

        # 2. Extract Money Patterns (e.g., $100 million, $5.5B, $1,000)
        # Regex looks for '$' followed by numbers, optional decimals, and optional suffixes (b/m/k/million/billion)
        money_pattern = r'\$\d+(?:,\d+)*(?:\.\d+)?\s?(?:billion|million|trillion|b|m|k)?'
        money_matches = re.findall(money_pattern, clean_text, re.IGNORECASE)

        # 3. Extract Percentage Patterns (e.g., 15%, 2.45%)
        # Regex looks for numbers followed immediately by '%'
        percent_pattern = r'\d+(?:\.\d+)?%'
        percent_matches = re.findall(percent_pattern, clean_text)

        # 4. Construct a summary for the LLM
        summary = (
            f"Investment Data Extraction Report:\n"
            f"- Total Financial Figures Detected: {len(money_matches)}\n"
            f"- Sample Figures: {', '.join(money_matches[:10])}...\n"
            f"- Key Ratios/Percentages Detected: {', '.join(percent_matches[:10])}...\n"
            f"- Data Readiness: Processed {len(clean_text)} characters for analysis."
        )
        
        return summary

    async def _arun(self, financial_data: str):
        return self._run(financial_data)

## Creating Risk Assessment Tool
class RiskInput(BaseModel):
    financial_data: str = Field(..., description="The text content of the financial report.")

class RiskTool(BaseTool):
    name: str = "Risk Assessment Calculator"
    description: str = "Scans financial text for risk indicators."
    args_schema: type[BaseModel] = RiskInput # <--- Link the schema here

    def _run(self, financial_data: str):        
        """
        Scans text for specific keywords indicating financial or operational risk.
        """
        # 1. Define Risk Keywords
        risk_keywords = [
            'debt', 'liability', 'default', 'litigation', 'lawsuit', 
            'regulation', 'compliance', 'investigation', 'inflation', 
            'volatility', 'risk', 'loss', 'decline', 'downside', 'uncertainty'
        ]
        
        # 2. Perform Frequency Analysis
        found_risks = {}
        lower_text = financial_data.lower()
        
        total_risk_hits = 0
        max_count = 0
        max_count_word = ""
        for word in risk_keywords:
            count = lower_text.count(word)
            if count > 0:
                found_risks[word] = count
                total_risk_hits += count
                if count>max_count:
                    max_count = count
                    max_count_word = word
        
        # 3. Generate Risk Score & Report
        if total_risk_hits == 0:
            return "Risk Assessment: No immediate red flags detected in keyword scan."
            
        risk_report = (
            f"Risk Assessment Scan:\n"
            f"- Total Risk Flags: {total_risk_hits}\n"
            f"- Breakdown: {found_risks}\n"
            f"- Recommendation: The Risk Assessor Agent should deeply investigate the sections containing '{max_count_word}'."
        )
        
        return risk_report

    async def _arun(self, financial_data: str):
        return self._run(financial_data)