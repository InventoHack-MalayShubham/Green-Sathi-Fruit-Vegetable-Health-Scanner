import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class USDAClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('USDA_KEY')
        if not self.api_key:
            raise ValueError("USDA_KEY not found in environment variables")
        self.nutrient_map = {
            "calories": ("Energy (kcal)", 1008),
            "protein": ("Protein", 1003),
            "carbs": ("Carbohydrate, by difference", 1005),
            "fiber": ("Fiber, total dietary", 1079),
            "sugars": ("Sugars, total including NLEA", 2000),
            "fat": ("Total lipid (fat)", 1004),
            "vitamin_c": ("Vitamin C, total ascorbic acid", 1162),
            "iron": ("Iron, Fe", 1089),
            "calcium": ("Calcium, Ca", 1087),
            "potassium": ("Potassium, K", 1092)
        }

    def get_nutrition(self, food_name):
        try:
            if not food_name:
                return None

            params = {
                "api_key": self.api_key,
                "query": food_name,
                "pageSize": 1,
                "dataType": ["Survey (FNDDS)"]
            }

            response = requests.get(
                "https://api.nal.usda.gov/fdc/v1/foods/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()

            if not response.json().get("foods"):
                return None

            return self._extract_nutrients(response.json()["foods"][0])

        except Exception as e:
            print(f"Nutrition API Error: {str(e)}")
            return None

    def _extract_nutrients(self, food_data):
        nutrients = food_data.get("foodNutrients", [])
        return {
            key: next(
                (n["value"] for n in nutrients if n["nutrientId"] == self.nutrient_map[key][1]),
                0.0
            )
            for key in self.nutrient_map
        } 