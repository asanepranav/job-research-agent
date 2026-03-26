"""
agent.py — Job Research Agent (modern LangChain LCEL approach)

Uses LangChain's tool-calling agent — cleaner, more reliable than ReAct string parsing.
The LLM natively calls tools as structured function calls (like GPT function calling).
"""

import os
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
from tools import search_jobs, search_company, extract_skills, draft_outreach_email


SYSTEM_PROMPT = """You are a smart job research assistant helping a recent BE graduate find Data Science / ML jobs in India.

For every research request, you MUST complete these 4 steps in order:
1. Search for job listings using search_jobs
2. Research 1-2 specific companies found using search_company  
3. Extract key skills from the listings using extract_skills
4. Draft a personalized outreach email using draft_outreach_email

Be thorough. Always complete all 4 steps before giving your final answer.
In your final answer, include:
- Top companies hiring for this role
- Most in-demand skills
- The drafted outreach email
"""


def run_agent(role: str, location: str, candidate_background: str) -> dict:
    """
    Run the job research agent using tool-calling loop.
    Returns final answer + all intermediate steps.
    """
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        max_tokens=4096,
    )

    tools = [search_jobs, search_company, extract_skills, draft_outreach_email]
    llm_with_tools = llm.bind_tools(tools)
    tool_map = {t.name: t for t in tools}

    task = f"""Research job opportunities for:
- Role: {role}
- Location: {location}
- My background: {candidate_background}

Complete all 4 steps: search jobs, research companies, extract skills, draft email."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": task}
    ]

    steps = []

    for i in range(10):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        for tool_call in response.tool_calls:
            tool_name  = tool_call["name"]
            tool_input = tool_call["args"]
            tool_id    = tool_call["id"]

            tool_fn = tool_map.get(tool_name)
            if tool_fn:
                try:
                    input_str = list(tool_input.values())[0] if tool_input else ""
                    observation = tool_fn.invoke(input_str)
                except Exception as e:
                    observation = f"Tool error: {str(e)}"
            else:
                observation = f"Unknown tool: {tool_name}"

            steps.append({
                "tool":   tool_name,
                "input":  str(tool_input),
                "output": str(observation)[:600],
            })

            messages.append(ToolMessage(
                content=str(observation),
                tool_call_id=tool_id
            ))

    final_answer = response.content if response.content else "Agent completed. See steps above."

    return {
        "final_answer": final_answer,
        "steps": steps,
    }
