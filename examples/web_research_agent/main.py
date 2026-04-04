"""
Web Research Agent with multiple specialized agents
"""

import asyncio
from typing import List, Dict
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from bs4 import BeautifulSoup
import json

class ResearchManagerAgent(Agent):
    """Orchestrates research tasks"""
    
    def __init__(self):
        llm = ChatOpenAI(model="gpt-4", temperature=0.5)
        super().__init__(
            role="Research Manager",
            goal="Coordinate research tasks and synthesize findings",
            backstory="Experienced research coordinator with PhD in Computer Science",
            llm=llm,
            verbose=True,
            tools=[DuckDuckGoSearchRun()]
        )

class WebScraperAgent(Agent):
    """Specialized in web scraping"""
    
    def __init__(self):
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        super().__init__(
            role="Web Scraper",
            goal="Extract information from websites efficiently",
            backstory="Web scraping expert with 8 years experience",
            llm=llm,
            verbose=True
        )
    
    async def scrape_url(self, url: str) -> str:
        """Scrape content from URL"""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text()[:5000]  # Limit output
        except Exception as e:
            return f"Error scraping {url}: {str(e)}"

class DataAnalyzerAgent(Agent):
    """Analyzes extracted data"""
    
    def __init__(self):
        llm = ChatOpenAI(model="gpt-4", temperature=0.4)
        super().__init__(
            role="Data Analyzer",
            goal="Analyze and structure extracted data",
            backstory="Data scientist specializing in information extraction",
            llm=llm,
            verbose=True
        )
    
    def analyze_data(self, data: str) -> Dict:
        """Analyze scraped data"""
        # Simple analysis - in reality would be more complex
        lines = data.split('\n')
        return {
            "line_count": len(lines),
            "word_count": len(data.split()),
            "char_count": len(data)
        }

class ReportGeneratorAgent(Agent):
    """Generates final reports"""
    
    def __init__(self):
        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        super().__init__(
            role="Report Generator",
            goal="Create comprehensive research reports",
            backstory="Technical writer with expertise in research documentation",
            llm=llm,
            verbose=True
        )
    
    def generate_report(self, findings: List[Dict]) -> str:
        """Generate report from findings"""
        report = "# Research Report\n\n"
        for i, finding in enumerate(findings, 1):
            report += f"## Finding {i}\n"
            report += f"{json.dumps(finding, indent=2)}\n\n"
        return report

async def main():
    """Main research workflow"""
    
    # Initialize agents
    manager = ResearchManagerAgent()
    scraper = WebScraperAgent()
    analyzer = DataAnalyzerAgent()
    reporter = ReportGeneratorAgent()
    
    # Define tasks
    manage_task = Task(
        description="Coordinate research on AI agent deployment trends",
        agent=manager,
        expected_output="List of key topics and sources to research"
    )
    
    scrape_task = Task(
        description="Scrape information from provided URLs",
        agent=scraper,
        expected_output="Raw extracted content from websites"
    )
    
    analyze_task = Task(
        description="Analyze the scraped content",
        agent=analyzer,
        expected_output="Structured analysis of the content"
    )
    
    report_task = Task(
        description="Generate final research report",
        agent=reporter,
        expected_output="Comprehensive PDF report"
    )
    
    # Create crew with sequential process
    crew = Crew(
        agents=[manager, scraper, analyzer, reporter],
        tasks=[manage_task, scrape_task, analyze_task, report_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute research
    print("Starting research crew...")
    result = await crew.kickoff()
    
    # Save results
    with open("research_report.md", "w") as f:
        f.write(str(result))
    
    print(f"Research complete! Report saved to research_report.md")
    return result

if __name__ == "__main__":
    asyncio.run(main())
