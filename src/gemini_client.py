"""
Gemini API client for answer generation.
Uses Gemini 2.5 Flash for grounded responses.
"""

import os
import time
from typing import Dict
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def generate_answer(query: str, context: str) -> Dict:
    """
    Generate grounded answer using Gemini 2.5 Flash.
    
    Args:
        query: User's question
        context: Retrieved and compressed KB context
        
    Returns:
        Dict with:
            - answer: Generated answer or "ESCALATE" if insufficient context
            - latency_ms: Generation latency
            - success: Whether generation succeeded
            - error: Error message if failed
    """
    if not GEMINI_API_KEY:
        return {
            "answer": "ESCALATE",
            "latency_ms": 0,
            "success": False,
            "error": "GEMINI_API_KEY not set"
        }
    
    start_time = time.time()
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""You are an IT helpdesk assistant. Answer the user's question using ONLY the KB snippets provided below.

CRITICAL RULES - STRICT GROUNDING:
1. Use ONLY the KB SNIPPETS below. Do NOT use any external knowledge, training data, or general information.
2. If the KB snippets do not contain sufficient information to answer the question safely and accurately, respond with exactly: "INSUFFICIENT"
3. Never make assumptions or fill in gaps with external knowledge
4. Be concise and helpful when KB has the answer
5. Include step-by-step instructions when they exist in the KB snippets
6. If you're uncertain whether the KB has enough info, respond with "INSUFFICIENT"

KB SNIPPETS:
{context}

USER QUESTION:
{query}

ANSWER (KB-only, or "INSUFFICIENT"):"""

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        answer = response.text.strip()
        
        return {
            "answer": answer,
            "latency_ms": latency_ms,
            "success": True,
            "error": None
        }
        
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "answer": "ESCALATE",
            "latency_ms": latency_ms,
            "success": False,
            "error": f"Exception: {str(e)}"
        }


if __name__ == "__main__":
    # Test answer generation
    test_context = """
    VPN Setup Guide:
    1. Download the VPN client from the IT portal
    2. Install the client on your device
    3. Open the VPN client and enter your credentials
    4. Connect to the corporate network
    """
    
    test_query = "How do I set up VPN?"
    
    result = generate_answer(test_query, test_context)
    print(f"Success: {result['success']}")
    print(f"Answer: {result['answer']}")
    print(f"Latency: {result['latency_ms']:.2f}ms")
    if result['error']:
        print(f"Error: {result['error']}")
