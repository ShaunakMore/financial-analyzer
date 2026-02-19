import os
from celery import Celery
from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import verification, analyze_financial_document, investment_analysis, risk_assessment

# Initialize Celery with Redis as the Broker
celery_app = Celery(
    "financial_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(name="run_financial_analysis")
def run_financial_analysis(query, file_path):
    crew = Crew(
        agents=[verifier,financial_analyst,investment_advisor,risk_assessor],
        tasks=[verification,analyze_financial_document,investment_analysis,risk_assessment],
        process=Process.sequential,
        #verbose=True
    )
    result = crew.kickoff({'query': query,'file_path':file_path})
    
    task_output = [task.raw for task in result.tasks_output]
    
    parsed_task_output = f"""
    \nANALYSIS:\n
     
    {task_output[1]}
    
    \nINVESTMENT INSIGHT:\n
    
    {task_output[2]}
    
    \nRISK ANALYSIS:\n
    
    {task_output[3]}
    """

    return parsed_task_output