import base64
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LllamaHealthAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('Lllama_KEY')
        if not self.api_key:
            raise ValueError("Lllama_KEY not found in environment variables")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Referer": "https://freshcheck-pro.com",  # Fixed header name
            "X-Title": "FreshCheck Pro"
        }
        self.timeout = 30

    def analyze_image(self, image_path):
        try:
            print(f"\n=== Analyzing image: {image_path} ===")
            
            # Read and encode image
            with open(image_path, "rb") as f:
                b64_image = base64.b64encode(f.read()).decode("utf-8")
                print("Image encoded successfully")

            prompt = """You are a produce quality analyzer. Analyze the image and return ONLY a valid JSON object with the following structure:
{
    "item": "name of the produce",
    "type": "fruit/vegetable/herb",
    "status": "fresh/rotten/uncertain",
    "confidence": 0.0-1.0,
    "issues": ["list", "of", "problems"],
    "storage_tips": "string"
}

Important: Do not include any additional text, markdown, or explanation. Only return the JSON object."""

            payload = {
                "model": "meta-llama/llama-4-maverick:free",  # Verified model
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}",
                            "detail": "auto"
                        }}
                    ]
                }]
            }

            print("Sending request to OpenRouter API...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            # Debug logging
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.text[:300]}...")  # Truncated for readability

            response.raise_for_status()
            return self._parse_response(response.json())

        except Exception as e:
            print(f"\n!!! API Error: {str(e)}")
            return self._error_response(e)

    def _parse_response(self, response):
        try:
            content = response["choices"][0]["message"]["content"]
            print(f"Raw API Response:\n{content}")
            
            # Clean JSON extraction
            json_str = content.strip().replace('```json', '').replace('```', '').strip()
            result = json.loads(json_str)
            
            # Validate response structure
            required_fields = ["item", "type", "status", "confidence", "issues", "storage_tips"]
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing field: {field}")
            
            print("Successfully parsed valid response")
            return result
            
        except Exception as e:
            print(f"JSON Parsing Error: {str(e)}")
            return self._error_response(e, parsing=True)

    def _error_response(self, error, parsing=False):
        error_type = "Parsing" if parsing else "API"
        return {
            "error": f"{error_type} Error: {str(error)}",
            "item": "Unable to analyze - Service Temporarily Unavailable",
            "type": "Unknown",
            "status": "uncertain",
            "confidence": 0.0,
            "issues": ["Technical Error"],
            "storage_tips": "Please try again later"
        }