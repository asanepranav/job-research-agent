"""
tools.py — Custom tools the agent can call

Each tool is a function decorated with @tool.
The agent reads the docstring to decide when to use it.
"""

from langchain_core.tools import tool
from tavily import TavilyClient
import os


def get_tavily():
    return TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))


@tool
def search_jobs(query: str) -> str:
    """
    Search the internet for job listings, company info, or industry news.
    Use this to find recent job postings, required skills, and company details.
    Input should be a specific search query like 'Data Scientist fintech startup India 2024'.
    """
    try:
        client = get_tavily()
        results = client.search(
            query=query,
            max_results=5,
            search_depth="advanced"
        )
        output = []
        for r in results.get("results", []):
            output.append(f"Title: {r.get('title', '')}")
            output.append(f"URL: {r.get('url', '')}")
            output.append(f"Content: {r.get('content', '')[:500]}")
            output.append("---")
        return "\n".join(output) if output else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def search_company(company_name: str) -> str:
    """
    Research a specific company — what they do, their tech stack, culture, and recent news.
    Use this after finding a company name in job listings to learn more about them.
    Input should be the company name, e.g. 'Razorpay' or 'Zepto'.
    """
    try:
        client = get_tavily()
        results = client.search(
            query=f"{company_name} company overview tech stack culture hiring 2024",
            max_results=3,
            search_depth="advanced"
        )
        output = [f"Research on {company_name}:\n"]
        for r in results.get("results", []):
            output.append(f"- {r.get('title', '')}: {r.get('content', '')[:400]}")
        return "\n".join(output)
    except Exception as e:
        return f"Company research error: {str(e)}"


@tool
def extract_skills(job_descriptions: str) -> str:
    """
    Analyze job descriptions and extract the key technical skills, tools, and requirements.
    Use this after collecting job listings to understand what skills are most in demand.
    Input should be raw job description text.
    """
    # This tool uses the LLM's own reasoning — it just structures the prompt
    # The agent will call this and pass results to its reasoning chain
    return f"""
    Please analyze these job descriptions and extract:
    1. Top 5 technical skills mentioned most often
    2. Common tools and frameworks required
    3. Experience level typically required
    4. Any specific domain knowledge needed

    Job descriptions to analyze:
    {job_descriptions[:2000]}
    """


@tool
def draft_outreach_email(context: str) -> str:
    """
    Draft a personalized cold outreach email to a company for a job opportunity.
    Use this as the final step after researching the company and understanding the role.
    Input should include: candidate background, company name, role, and why they're a good fit.
    """
    return f"""
    Please write a professional cold outreach email with:
    - Subject line
    - Brief intro (2 sentences max)
    - Why interested in THIS company specifically (use research)
    - 2-3 relevant skills/projects that match their needs
    - Clear call to action
    - Professional sign-off

    Keep it under 200 words. Make it personal, not generic.

    Context to use:
    {context}
    """
