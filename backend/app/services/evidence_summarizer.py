import json
import os
from typing import List, Dict, Any

async def summarize_evidence(drug_name: str, disease_name: str, papers: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Returns:
    {
      "overall_summary": str,
      "points": list[str]
    }
    """
    fallback = {
        "overall_summary": "Evidence summary temporarily unavailable.",
        "points": []
    }

    try:
        # Construct plain text for the prompt
        evidence_text = ""
        for p in papers:
            evidence_text += f"Title: {p['title']}\nLink: {p.get('url', 'N/A')}\nAbstract: {p['abstract']}\n\n"

        if not evidence_text.strip():
             return {
                "overall_summary": "No abstracts available to summarize.",
                "points": []
            }

        prompt = f"""
        You are a biomedical AI assistant.
        Task: Summarize the relationship between {drug_name} and {disease_name} based ONLY on the provided evidence.
        
        Evidence:
        {evidence_text}
        
        Instructions:
        1. Do not invent information.
        2. Use only the provided abstracts as evidence.
        3. Include specific Paper Links in your summary where relevant (e.g. "Study X (Link) showed...").
        4. Output MUST be valid JSON only.
        
        Format:
        {{
            "overall_summary": "Strictly 2-3 sentences summarizing key findings...",
            "points": ["point 1", "point 2", "point 3"]
        }}
        """

        # Switch to Google Gemini
        if os.getenv("GOOGLE_API_KEY"):
            import google.generativeai as genai
            
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = await model.generate_content_async(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
            except Exception:
                # Fallback to gemini-2.0-flash-exp
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = await model.generate_content_async(prompt)
            
            content = response.text
            return json.loads(content)
            
        else:
             return fallback

    except Exception:
        import traceback
        with open("gemini_error.txt", "w") as f:
            traceback.print_exc(file=f)
        return fallback
