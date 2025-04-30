import base64
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class GeminiHealthAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_KEY not found in environment variables")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://freshcheck-pro.com",
            "X-Title": "FreshCheck Pro"
        }
        self.timeout = 30
    def analyze_image(self, image_path):
        try:
            with open(image_path, "rb") as f:
                b64_image = base64.b64encode(f.read()).decode("utf-8")

            prompt = """You are a produce quality analyzer. Analyze the image and return ONLY a valid JSON object with the following structure:
{
    "item": "name of the produce",
    "type": "fruit/vegetable/herb",
    "status": "fresh/rotten/uncertain",
    "confidence": 0.0-1.0,
    "issues": ["list", "of", "problems"],
    "storage_tips": "string"
}

Do not include any additional text or explanation. Only return the JSON object."""

            payload = {
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                        ]
                    }
                ]
            }

            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return self._parse_response(response.json())

        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return {
                "error": f"Gemini API Error: {str(e)}",
                "item": "Sorry for incovinience, free trials have exhausted, trials will be refereshed at 5:00 AM. Unable to identify the item at the moment.",
                "type": "Unknown",
                "status": "uncertain",
                "confidence": 0.0,
                "issues": ["API Error"],
                "storage_tips": "Unable to analyze due to technical issues"
            }

    def _parse_response(self, response):
        try:
            content = response["choices"][0]["message"]["content"]
            # Try to find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON object found in response")
            
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["item", "type", "status", "confidence", "issues", "storage_tips"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except Exception as e:
            print(f"Response Parsing Error: {str(e)}")
            return {
                "error": f"Failed to parse response: {str(e)}",
                "item": "Unknown",
                "type": "Unknown",
                "status": "uncertain",
                "confidence": 0.0,
                "issues": ["Parsing Error"],
                "storage_tips": "Unable to analyze due to technical issues"
            } 
