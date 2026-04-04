"""
Simple CrewAI agent example for deployment testing
"""

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import pandas as pd
import numpy as np

class DataAnalystAgent(Agent):
    """Agent for analyzing data"""
    
    def __init__(self):
        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        super().__init__(
            role="Data Analyst",
            goal="Analyze datasets and extract insights",
            backstory="Expert data scientist with 10 years experience",
            llm=llm,
            verbose=True
        )
    
    def analyze_data(self, data_path: str):
        """Analyze data from CSV file"""
        data = pd.read_csv(data_path)
        summary = data.describe()
        return summary

class ReportWriterAgent(Agent):
    """Agent for writing reports"""
    
    def __init__(self):
        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        super().__init__(
            role="Report Writer",
            goal="Create comprehensive reports from analysis",
            backstory="Technical writer specializing in data reports",
            llm=llm,
            verbose=True
        )
    
    def write_report(self, analysis_results):
        """Write report based on analysis"""
        report = f"Analysis Summary:\n{analysis_results}"
        return report

def main():
    # Create agents
    analyst = DataAnalystAgent()
    writer = ReportWriterAgent()
    
    # Create tasks
    analyze_task = Task(
        description="Analyze the sales_data.csv file",
        agent=analyst,
        expected_output="Statistical summary of the data"
    )
    
    write_task = Task(
        description="Write a report based on the analysis",
        agent=writer,
        expected_output="Comprehensive report document"
    )
    
    # Create crew
    crew = Crew(
        agents=[analyst, writer],
        tasks=[analyze_task, write_task],
        verbose=True
    )
    
    # Run crew
    result = crew.kickoff()
    print(result)

if __name__ == "__main__":
    main()
