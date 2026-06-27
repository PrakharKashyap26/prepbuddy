import requests
from typing import List, Dict
import config

def get_courses(skill: str, topic: str) -> List[Dict]:
    """
    Search courses using Google Custom Search API.
    If credentials are not configured, returns a mock course listing matching the query.
    """
    api_key = config.GOOGLE_API_KEY
    cse_id = config.GOOGLE_CSE_ID
    
    # Verify environment keys are configured properly
    if not api_key or not cse_id or "AIza" not in api_key or cse_id == "your_cse_id_here":
        return get_mock_courses(skill, topic)
        
    url = "https://www.googleapis.com/customsearch/v1"
    query = f"free online course tutorial for {skill} {topic}"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", f"{skill} Resource"),
                "description": item.get("snippet", "Detailed learning path tutorial resources."),
                "url": item.get("link", "#")
            })
        return results
    except Exception as e:
        print(f"Error querying Google Custom Search API: {e}. Falling back to mock courses.")
        return get_mock_courses(skill, topic)


def get_mock_courses(skill: str, topic: str) -> List[Dict]:
    """Generates premium mock courses matching the skill/topic."""
    return [
        {
            "title": f"Introduction to {skill} - Masterclass on {topic}",
            "description": f"Learn the core foundations of {skill} and deep-dive into {topic}. Features step-by-step guides, Socratic coding challenges, and exercises.",
            "url": f"https://www.coursera.org/search?query={skill}%20{topic}"
        },
        {
            "title": f"Ultimate {skill} Training Course: Focus on {topic}",
            "description": f"Master the practical tools in {skill} with real-world scenarios in {topic}. Ideal for junior developers planning technical interviews.",
            "url": f"https://www.udemy.com/courses/search/?q={skill}%20{topic}"
        },
        {
            "title": f"Free Code Camp - {skill} {topic} Complete Walkthrough",
            "description": f"Comprehensive free tutorial walkthrough outlining practical patterns, syntax rules, and error-handling techniques for {skill}.",
            "url": f"https://www.youtube.com/results?search_query=freecodecamp+{skill}+{topic}"
        }
    ]
