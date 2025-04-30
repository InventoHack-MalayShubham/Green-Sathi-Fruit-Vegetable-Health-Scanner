import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DeepSeekRecommender:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_recommendations(self, user_data):
        prompt = f"""
I am {user_data['weight']} kg, my height is {user_data['height']} feet, my diet plan is {user_data['diet_plan']}, I am from {user_data['region']}, 
I am currently eating {user_data['current_fruit']}.
Based on the present season, my locality, BMI, and diet plan,
Tell me 5 fruits I should eat to complete my nutrient level and follow my diet chart.
Just give names and reasons—nothing else.
I know the nutrient value of {user_data['current_fruit']}, so skip that but explain how it's beneficial and any precautions.

Keep it concise.

Give all the answers in english only.
"""
        try:
            response = requests.post(
                url=self.base_url,
                headers=self.headers,
                json={
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Check if the response has the expected structure
            if 'choices' not in data or not data['choices']:
                return "No recommendations available at the moment."
            
            content = data['choices'][0].get('message', {}).get('content', '')
            if not content:
                return "No recommendations available at the moment."
                
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {str(e)}")
            return "Unable to generate recommendations at the moment."
        except (KeyError, ValueError, AttributeError) as e:
            print(f"Response Parsing Error: {str(e)}")
            return "Error processing recommendations."
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            return "An unexpected error occurred while generating recommendations." 