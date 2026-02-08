"""
ScaleDown API client for text compression.
Compresses text targeting gemini-2.5-flash model.
"""

import os
import requests
import time
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

SCALEDOWN_API_URL = "https://api.scaledown.xyz/compress/raw/"
SCALEDOWN_API_KEY = os.getenv("SCALEDOWN_API_KEY")


def compress_text(text: str, target_model: str = "gemini-2.5-flash") -> Dict:
    """
    Compress text using ScaleDown API.
    
    Args:
        text: Text to compress
        target_model: Target model for compression optimization
        
    Returns:
        Dict with:
            - compressed_text: Compressed text
            - original_tokens: Original token count
            - compressed_tokens: Compressed token count
            - compression_ratio: Ratio of compression
            - original_words: Original word count
            - compressed_words: Compressed word count
            - latency_ms: API latency in milliseconds
            - success: Whether compression succeeded
            - error: Error message if failed
    """
    if not SCALEDOWN_API_KEY:
        return {
            "compressed_text": text,
            "original_tokens": len(text.split()),
            "compressed_tokens": len(text.split()),
            "compression_ratio": 1.0,
            "original_words": len(text.split()),
            "compressed_words": len(text.split()),
            "latency_ms": 0,
            "success": False,
            "error": "SCALEDOWN_API_KEY not set"
        }
    
    start_time = time.time()
    
    try:
        headers = {
            "x-api-key": SCALEDOWN_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "target_model": target_model
        }
        
        response = requests.post(
            SCALEDOWN_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract metrics from ScaleDown response
            compressed_text = data.get("compressed_text", text)
            original_tokens = data.get("original_tokens", len(text.split()))
            compressed_tokens = data.get("compressed_tokens", len(compressed_text.split()))
            
            return {
                "compressed_text": compressed_text,
                "original_tokens": original_tokens,
                "compressed_tokens": compressed_tokens,
                "compression_ratio": original_tokens / max(compressed_tokens, 1),
                "original_words": len(text.split()),
                "compressed_words": len(compressed_text.split()),
                "latency_ms": latency_ms,
                "success": True,
                "error": None
            }
        else:
            return {
                "compressed_text": text,
                "original_tokens": len(text.split()),
                "compressed_tokens": len(text.split()),
                "compression_ratio": 1.0,
                "original_words": len(text.split()),
                "compressed_words": len(text.split()),
                "latency_ms": latency_ms,
                "success": False,
                "error": f"API error: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "compressed_text": text,
            "original_tokens": len(text.split()),
            "compressed_tokens": len(text.split()),
            "compression_ratio": 1.0,
            "original_words": len(text.split()),
            "compressed_words": len(text.split()),
            "latency_ms": latency_ms,
            "success": False,
            "error": f"Exception: {str(e)}"
        }


if __name__ == "__main__":
    # Test compression
    test_text = """
    To reset your password, follow these steps:
    1. Go to the login page
    2. Click 'Forgot Password'
    3. Enter your email address
    4. Check your email for reset link
    5. Click the link and create a new password
    """
    
    result = compress_text(test_text)
    print(f"Success: {result['success']}")
    print(f"Original tokens: {result['original_tokens']}")
    print(f"Compressed tokens: {result['compressed_tokens']}")
    print(f"Compression ratio: {result['compression_ratio']:.2f}x")
    print(f"Latency: {result['latency_ms']:.2f}ms")
    if result['error']:
        print(f"Error: {result['error']}")
