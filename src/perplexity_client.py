import requests
import os
import json
from typing import List, Dict, Any, Optional

class PerplexitySonarClient:
    def __init__(self, api_key=None, model="sonar-pro"):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.model = model
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Simple completion method for compatibility with CrewAI"""
        messages = [{"role": "user", "content": prompt}]
        response = self.generate(messages)
        return response["choices"][0]["message"]["content"]
        
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7, stream: bool = False) -> Dict[str, Any]:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
