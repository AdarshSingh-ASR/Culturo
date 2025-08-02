import logging
import json
from typing import Dict, Any, Optional
from ..config import settings
from ..shared.errors import ExternalServiceError

logger = logging.getLogger(__name__)

class FoodAnalysisService:
    """Service for analyzing food based on name input using Qloo and LLM"""
    
    def __init__(self, llm_service, qloo_service):
        self.llm_service = llm_service
        self.qloo_service = qloo_service
        
        # Common food categories for classification
        self.food_categories = {
            "main_dish": ["pizza", "pasta", "curry", "burger", "steak", "chicken", "fish", "rice", "noodles"],
            "appetizer": ["bruschetta", "spring roll", "samosa", "hummus", "guacamole", "cheese plate"],
            "dessert": ["tiramisu", "cake", "ice cream", "cookie", "brownie", "pie", "cheesecake"],
            "beverage": ["coffee", "tea", "juice", "smoothie", "wine", "beer", "cocktail"],
            "snack": ["chips", "nuts", "popcorn", "crackers", "dried fruit"],
            "soup": ["tomato soup", "chicken soup", "miso soup", "lentil soup", "clam chowder"],
            "salad": ["caesar salad", "greek salad", "cobb salad", "garden salad", "tabbouleh"],
            "bread": ["sourdough", "baguette", "naan", "pita bread", "focaccia"],
            "pasta": ["spaghetti", "fettuccine", "penne", "ravioli", "lasagna"],
            "seafood": ["salmon", "tuna", "shrimp", "lobster", "crab", "oysters"],
            "meat": ["beef", "pork", "lamb", "duck", "turkey", "bacon"],
            "vegetarian": ["tofu", "tempeh", "quinoa", "lentils", "chickpeas"],
            "vegan": ["tofu", "tempeh", "quinoa", "lentils", "chickpeas", "almond milk"]
        }
        
        # Cuisine type mapping
        self.cuisine_mapping = {
            "italian": ["pizza", "pasta", "risotto", "bruschetta", "tiramisu", "focaccia"],
            "japanese": ["sushi", "ramen", "tempura", "miso soup", "sashimi", "udon"],
            "indian": ["curry", "naan", "samosa", "biryani", "tandoori", "dal"],
            "mexican": ["taco", "burrito", "enchilada", "quesadilla", "guacamole", "salsa"],
            "chinese": ["dim sum", "kung pao", "sweet and sour", "chow mein", "fried rice"],
            "thai": ["pad thai", "tom yum", "green curry", "massaman curry", "som tam"],
            "mediterranean": ["hummus", "falafel", "kebab", "gyro", "tabbouleh", "tzatziki"],
            "american": ["burger", "hot dog", "sandwich", "fries", "apple pie", "cheesecake"],
            "french": ["croissant", "quiche", "ratatouille", "coq au vin", "creme brulee"],
            "korean": ["bibimbap", "bulgogi", "kimchi", "japchae", "tteokbokki"],
            "vietnamese": ["pho", "banh mi", "spring rolls", "bun cha", "com tam"],
            "greek": ["moussaka", "souvlaki", "spanakopita", "baklava", "tzatziki"],
            "turkish": ["kebab", "lahmacun", "pide", "baklava", "ayran"],
            "moroccan": ["tagine", "couscous", "harira", "pastilla", "mint tea"],
            "lebanese": ["shawarma", "falafel", "tabbouleh", "hummus", "baklava"]
        }
    
    async def analyze_food_by_name(self, food_name: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Analyze food based on name input using Qloo and LLM"""
        try:
            # Normalize food name
            normalized_food_name = self._normalize_food_name(food_name)
            
            # Get cultural context from Qloo
            cultural_data = await self._get_cultural_context(normalized_food_name)
            
            # Get nutritional information from Qloo
            nutrition_data = await self._get_nutritional_info(normalized_food_name)
            
            # Generate comprehensive analysis using LLM
            analysis_data = await self._generate_comprehensive_analysis(
                normalized_food_name, cultural_data, nutrition_data
            )
            
            return {
                "food_name": normalized_food_name,
                "confidence_score": 1.0,  # Since we have the exact name
                "category": analysis_data["category"],
                "cuisine_type": analysis_data["cuisine_type"],
                "nutrition": nutrition_data,
                "cultural_context": cultural_data,
                "ingredients": analysis_data["ingredients"],
                "recipe": analysis_data["recipe"],
                "recommendations": analysis_data["recommendations"],
                "health_benefits": analysis_data["health_benefits"],
                "dietary_restrictions": analysis_data["dietary_restrictions"],
                "allergens": analysis_data["allergens"]
            }
            
        except Exception as e:
            logger.error(f"Food analysis failed for {food_name}: {str(e)}")
            raise ExternalServiceError(
                service="Food Analysis Service",
                message=f"Analysis failed for {food_name}: {str(e)}"
            )
    
    def _normalize_food_name(self, food_name: str) -> str:
        """Normalize food name for consistent processing"""
        # Convert to lowercase and replace spaces with underscores
        normalized = food_name.lower().strip().replace(" ", "_")
        
        # Remove special characters except underscores
        import re
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        
        return normalized
    
    async def _get_cultural_context(self, food_name: str) -> Dict[str, Any]:
        """Get cultural context from Qloo API"""
        try:
            cultural_data = await self.qloo_service.get_food_cultural_context(food_name)
            # Transform the data to match expected format
            return {
                "origin_country": cultural_data.get("origin", "Various origins"),
                "origin_region": "International",
                "historical_significance": cultural_data.get("cultural_significance", f"{food_name.replace('_', ' ')} has cultural significance"),
                "traditional_occasions": cultural_data.get("traditional_occasions", ["Family meals", "Celebrations"]),
                "cultural_symbolism": "Represents cultural heritage",
                "preparation_methods": cultural_data.get("preparation_methods", ["Traditional cooking", "Modern preparation"]),
                "serving_traditions": ["Family style", "Individual portions"]
            }
        except Exception as e:
            logger.warning(f"Qloo cultural context failed for {food_name}: {str(e)}")
            # Fallback to default cultural data
            return {
                "origin_country": "Various origins",
                "origin_region": "International",
                "historical_significance": f"{food_name.replace('_', ' ')} has cultural significance",
                "traditional_occasions": ["Family meals", "Celebrations"],
                "cultural_symbolism": "Represents cultural heritage",
                "preparation_methods": ["Traditional cooking", "Modern preparation"],
                "serving_traditions": ["Family style", "Individual portions"]
            }
    
    async def _get_nutritional_info(self, food_name: str) -> Dict[str, Any]:
        """Get nutritional information from Qloo API"""
        try:
            nutrition_data = await self.qloo_service.get_nutritional_info(food_name)
            # Transform the data to match expected format
            return {
                "calories": nutrition_data.get("calories", 300),
                "protein": nutrition_data.get("protein", 15.0),
                "carbohydrates": nutrition_data.get("carbohydrates", 45.0),
                "fat": nutrition_data.get("fat", 10.0),
                "fiber": nutrition_data.get("fiber", 5.0),
                "sugar": nutrition_data.get("sugar", 8.0),
                "sodium": nutrition_data.get("sodium", 500),
                "allergens": nutrition_data.get("allergens", []),
                "health_benefits": nutrition_data.get("health_benefits", ["Provides essential nutrients"])
            }
        except Exception as e:
            logger.warning(f"Qloo nutritional info failed for {food_name}: {str(e)}")
            # Fallback to default nutritional data
            return {
                "calories": 300,
                "protein": 15.0,
                "carbohydrates": 45.0,
                "fat": 10.0,
                "fiber": 5.0,
                "sugar": 8.0,
                "sodium": 500,
                "allergens": [],
                "health_benefits": ["Provides essential nutrients"]
            }
    
    async def _generate_comprehensive_analysis(self, food_name: str, cultural_data: Dict, nutrition_data: Dict) -> Dict[str, Any]:
        """Generate comprehensive analysis using LLM"""
        try:
            # Create detailed prompt for LLM analysis
            prompt = f"""
            Analyze the food item "{food_name}" and provide comprehensive insights in JSON format:
            
            Food Information:
            - Name: {food_name}
            - Cultural Data: {cultural_data}
            - Nutritional Data: {nutrition_data}
            
            Please provide analysis in this JSON structure:
            {{
                "category": "main_dish|appetizer|dessert|beverage|snack|soup|salad|bread|pasta|seafood|meat|vegetarian|vegan",
                "cuisine_type": "italian|indian|mexican|chinese|japanese|american|french|mediterranean|thai|korean|vietnamese|greek|turkish|moroccan|lebanese",
                "ingredients": [
                    {{
                        "name": "ingredient name",
                        "quantity": "amount",
                        "category": "protein|vegetable|grain|dairy|spice|other",
                        "nutritional_contribution": "what this ingredient contributes"
                    }}
                ],
                "recipe": {{
                    "title": "recipe title",
                    "description": "detailed description",
                    "ingredients": [same structure as above],
                    "instructions": ["step1", "step2", "step3"],
                    "cooking_time": "time estimate",
                    "difficulty_level": "easy|medium|hard",
                    "servings": number,
                    "cuisine_type": "cuisine type"
                }},
                "recommendations": [
                    {{
                        "food_name": "recommended food",
                        "reason": "why this is recommended",
                        "similarity_score": 0.0-1.0,
                        "cultural_connection": "cultural relationship",
                        "nutritional_benefit": "nutritional advantage"
                    }}
                ],
                "health_benefits": ["benefit1", "benefit2"],
                "dietary_restrictions": ["restriction1", "restriction2"],
                "allergens": ["allergen1", "allergen2"]
            }}
            
            Base your analysis on the provided cultural and nutritional data, but enhance it with your knowledge.
            Be specific and accurate about the food item.
            """
            
            # Get LLM analysis
            llm_response = await self.llm_service.generate_response(
                prompt,
                max_tokens=2000,
                temperature=0.3,
                enforce_json=True
            )
            
            # Parse LLM response
            analysis_data = self._parse_llm_analysis(llm_response, food_name, cultural_data, nutrition_data)
            return analysis_data
            
        except Exception as e:
            logger.warning(f"LLM analysis failed for {food_name}: {str(e)}, using fallback")
            # Fallback to rule-based analysis
            return self._generate_rule_based_analysis(food_name, cultural_data, nutrition_data)
    
    def _parse_llm_analysis(self, llm_response: str, food_name: str, cultural_data: Dict, nutrition_data: Dict) -> Dict[str, Any]:
        """Parse LLM response for food analysis"""
        try:
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in LLM response")
            
            # Extract and validate data
            category = result.get("category", self._determine_category(food_name))
            cuisine_type = result.get("cuisine_type", self._determine_cuisine(food_name))
            
            # Ingredients
            ingredients = result.get("ingredients", [])
            if not ingredients:
                ingredients = self._generate_default_ingredients(food_name)
            
            # Recipe
            recipe_data = result.get("recipe", {})
            recipe = None
            if recipe_data:
                recipe = {
                    "title": recipe_data.get("title", f"Traditional {food_name.replace('_', ' ')}"),
                    "description": recipe_data.get("description", f"Authentic recipe for {food_name.replace('_', ' ')}"),
                    "ingredients": recipe_data.get("ingredients", ingredients),
                    "instructions": recipe_data.get("instructions", ["Prepare ingredients", "Cook according to tradition", "Serve hot"]),
                    "cooking_time": recipe_data.get("cooking_time", "30-45 minutes"),
                    "difficulty_level": recipe_data.get("difficulty_level", "medium"),
                    "servings": recipe_data.get("servings", 4),
                    "cuisine_type": recipe_data.get("cuisine_type", cuisine_type)
                }
            
            # Recommendations
            recommendations = result.get("recommendations", [])
            if not recommendations:
                recommendations = self._generate_default_recommendations(food_name)
            
            # Health benefits and restrictions
            health_benefits = result.get("health_benefits", self._generate_health_benefits(food_name))
            dietary_restrictions = result.get("dietary_restrictions", self._generate_dietary_restrictions(food_name))
            allergens = result.get("allergens", self._generate_allergens(food_name))
            
            return {
                "category": category,
                "cuisine_type": cuisine_type,
                "ingredients": ingredients,
                "recipe": recipe,
                "recommendations": recommendations,
                "health_benefits": health_benefits,
                "dietary_restrictions": dietary_restrictions,
                "allergens": allergens
            }
            
        except Exception as e:
            logger.error(f"Failed to parse LLM food analysis: {str(e)}")
            # Fallback to rule-based analysis
            return self._generate_rule_based_analysis(food_name, cultural_data, nutrition_data)
    
    def _generate_rule_based_analysis(self, food_name: str, cultural_data: Dict, nutrition_data: Dict) -> Dict[str, Any]:
        """Generate rule-based analysis as fallback"""
        category = self._determine_category(food_name)
        cuisine_type = self._determine_cuisine(food_name)
        ingredients = self._generate_default_ingredients(food_name)
        recommendations = self._generate_default_recommendations(food_name)
        health_benefits = self._generate_health_benefits(food_name)
        dietary_restrictions = self._generate_dietary_restrictions(food_name)
        allergens = self._generate_allergens(food_name)
        
        recipe = {
            "title": f"Traditional {food_name.replace('_', ' ')}",
            "description": f"Authentic recipe for {food_name.replace('_', ' ')} with cultural significance",
            "ingredients": ingredients,
            "instructions": [
                "Prepare the main ingredients",
                "Follow traditional cooking methods",
                "Season to taste",
                "Serve with cultural accompaniments"
            ],
            "cooking_time": "30-45 minutes",
            "difficulty_level": "medium",
            "servings": 4,
            "cuisine_type": cuisine_type
        }
        
        return {
            "category": category,
            "cuisine_type": cuisine_type,
            "ingredients": ingredients,
            "recipe": recipe,
            "recommendations": recommendations,
            "health_benefits": health_benefits,
            "dietary_restrictions": dietary_restrictions,
            "allergens": allergens
        }
    
    def _determine_category(self, food_name: str) -> str:
        """Determine food category based on name"""
        food_name_lower = food_name.lower()
        
        for category, foods in self.food_categories.items():
            if any(food in food_name_lower for food in foods):
                return category
        
        return "main_dish"  # Default category
    
    def _determine_cuisine(self, food_name: str) -> str:
        """Determine cuisine type based on name"""
        food_name_lower = food_name.lower()
        
        for cuisine, foods in self.cuisine_mapping.items():
            if any(food in food_name_lower for food in foods):
                return cuisine
        
        return "american"  # Default cuisine
    
    def _generate_default_ingredients(self, food_name: str) -> list:
        """Generate default ingredients based on food name"""
        food_name_lower = food_name.lower()
        
        if "pizza" in food_name_lower:
            return [
                {"name": "Pizza dough", "quantity": "1 base", "category": "grain"},
                {"name": "Tomato sauce", "quantity": "1/2 cup", "category": "vegetable"},
                {"name": "Mozzarella cheese", "quantity": "1 cup", "category": "dairy"},
                {"name": "Fresh basil", "quantity": "1/4 cup", "category": "herb"}
            ]
        elif "sushi" in food_name_lower:
            return [
                {"name": "Sushi rice", "quantity": "2 cups", "category": "grain"},
                {"name": "Fresh fish", "quantity": "8 oz", "category": "protein"},
                {"name": "Nori sheets", "quantity": "4 sheets", "category": "seaweed"},
                {"name": "Rice vinegar", "quantity": "2 tbsp", "category": "condiment"}
            ]
        elif "curry" in food_name_lower:
            return [
                {"name": "Curry spices", "quantity": "2 tbsp", "category": "spice"},
                {"name": "Coconut milk", "quantity": "1 can", "category": "liquid"},
                {"name": "Vegetables", "quantity": "2 cups", "category": "vegetable"},
                {"name": "Rice", "quantity": "1 cup", "category": "grain"}
            ]
        else:
            return [
                {"name": f"Main ingredient: {food_name.replace('_', ' ')}", "quantity": "1 serving", "category": "main"},
                {"name": "Seasonings", "quantity": "to taste", "category": "spice"},
                {"name": "Cooking oil", "quantity": "1 tbsp", "category": "fat"}
            ]
    
    def _generate_default_recommendations(self, food_name: str) -> list:
        """Generate default recommendations"""
        return [
            {
                "food_name": f"{food_name.replace('_', ' ')}",
                "reason": "Enjoy this culturally significant dish",
                "similarity_score": 0.8,
                "cultural_connection": "Cultural heritage",
                "nutritional_benefit": "Traditional nutrition"
            }
        ]
    
    def _generate_health_benefits(self, food_name: str) -> list:
        """Generate health benefits based on food type"""
        food_name_lower = food_name.lower()
        
        if any(word in food_name_lower for word in ['vegetable', 'salad']):
            return [
                "Rich in vitamins and minerals",
                "High in dietary fiber",
                "Low in calories",
                "Antioxidant properties"
            ]
        elif any(word in food_name_lower for word in ['fish', 'seafood']):
            return [
                "High in omega-3 fatty acids",
                "Excellent source of protein",
                "Heart-healthy",
                "Supports brain function"
            ]
        elif any(word in food_name_lower for word in ['meat', 'chicken']):
            return [
                "High-quality protein source",
                "Rich in B vitamins",
                "Good source of iron",
                "Contains essential amino acids"
            ]
        else:
            return ["Provides essential nutrients", "Energy source", "Cultural significance"]
    
    def _generate_dietary_restrictions(self, food_name: str) -> list:
        """Generate dietary restrictions based on food type"""
        food_name_lower = food_name.lower()
        restrictions = []
        
        if any(word in food_name_lower for word in ['meat', 'chicken', 'beef']):
            restrictions.extend(["Not suitable for vegetarians", "Not suitable for vegans"])
        elif any(word in food_name_lower for word in ['cheese', 'dairy', 'milk']):
            restrictions.extend(["Not suitable for vegans", "May contain lactose"])
        elif any(word in food_name_lower for word in ['fish', 'seafood']):
            restrictions.extend(["Not suitable for vegetarians", "Not suitable for vegans"])
        
        return restrictions
    
    def _generate_allergens(self, food_name: str) -> list:
        """Generate allergens based on food type"""
        food_name_lower = food_name.lower()
        allergens = []
        
        if any(word in food_name_lower for word in ['nuts', 'peanut']):
            allergens.append("Tree nuts")
        elif any(word in food_name_lower for word in ['seafood', 'fish', 'shrimp']):
            allergens.append("Fish/Shellfish")
        elif any(word in food_name_lower for word in ['wheat', 'bread', 'pasta']):
            allergens.append("Gluten")
        elif any(word in food_name_lower for word in ['cheese', 'milk', 'dairy']):
            allergens.append("Milk")
        elif any(word in food_name_lower for word in ['eggs']):
            allergens.append("Eggs")
        
        return allergens 