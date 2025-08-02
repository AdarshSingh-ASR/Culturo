import httpx
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from ..config import settings
from ..shared.errors import LLMServiceError, ExternalServiceError

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key
        self.openai_api_key = settings.openai_api_key
        self.openrouter_api_key = settings.openrouter_api_key
        self.default_provider = "gemini"  # Can be gemini, openai, openrouter
        
        # Set default provider based on available API keys
        if not self.gemini_api_key and not self.openai_api_key and not self.openrouter_api_key:
            logger.warning("No LLM API keys configured. Using fallback mode.")
            self.default_provider = "fallback"
        elif not self.gemini_api_key:
            if self.openai_api_key:
                self.default_provider = "openai"
            elif self.openrouter_api_key:
                self.default_provider = "openrouter"
        
    async def generate_response(
        self, 
        prompt: str, 
        provider: str = None,
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: str = None,
        enforce_json: bool = False
    ) -> str:
        """Generate response using specified LLM provider"""
        provider = provider or self.default_provider
        
        try:
            if provider == "fallback":
                return self._generate_basic_response(prompt)
            elif provider == "gemini":
                if not self.gemini_api_key:
                    raise ValueError("Gemini API key not configured")
                response = await self._call_gemini(prompt, model, max_tokens, temperature)
                if enforce_json:
                    return self._extract_json_from_response(response)
                return response
            elif provider == "openai":
                if not self.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                response = await self._call_openai(prompt, model, max_tokens, temperature, system_prompt)
                if enforce_json:
                    return self._extract_json_from_response(response)
                return response
            elif provider == "openrouter":
                if not self.openrouter_api_key:
                    raise ValueError("OpenRouter API key not configured")
                response = await self._call_openrouter(prompt, model, max_tokens, temperature, system_prompt)
                if enforce_json:
                    return self._extract_json_from_response(response)
                return response
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"LLM generation failed with provider {provider}: {str(e)}")
            # Try fallback to a different provider
            try:
                response = await self._fallback_generation(prompt, provider, enforce_json)
                return response
            except Exception as fallback_error:
                logger.error(f"Fallback generation also failed: {str(fallback_error)}")
                raise LLMServiceError(
                    provider=provider,
                    message="All LLM providers failed",
                    original_error=str(e)
                )
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from LLM response, handling various formats"""
        import re
        
        # Clean the response - remove markdown formatting
        cleaned_response = response.strip()
        
        # Try to find JSON in the response with more specific patterns
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # JSON in code block with json language
            r'```\s*(\{.*?\})\s*```',  # JSON in generic code block
            r'```\s*(\[.*?\])\s*```',  # JSON array in code block
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested JSON object
            r'\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]',  # JSON array with objects
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, cleaned_response, re.DOTALL)
            if matches:
                for match in matches:
                    try:
                        # Try to parse the JSON to validate it
                        parsed = json.loads(match)
                        # If it's a valid JSON object with expected fields, return it
                        if isinstance(parsed, dict) and len(parsed) > 0:
                            return match
                    except json.JSONDecodeError:
                        continue
        
        # If no valid JSON found, try to extract the last JSON-like structure
        try:
            # Find the last occurrence of a JSON-like structure
            last_brace = cleaned_response.rfind('{')
            last_bracket = cleaned_response.rfind('}')
            
            if last_brace != -1 and last_bracket != -1 and last_bracket > last_brace:
                potential_json = cleaned_response[last_brace:last_bracket + 1]
                # Try to fix common JSON issues
                potential_json = self._fix_common_json_issues(potential_json)
                json.loads(potential_json)  # Validate
                return potential_json
        except (json.JSONDecodeError, ValueError):
            pass
        
        # If all else fails, return a basic JSON structure
        logger.warning("Could not extract valid JSON from LLM response")
        return '{"error": "Could not parse JSON response", "raw_response": "' + response[:200] + '..."}'
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues"""
        # Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix unquoted keys
        json_str = re.sub(r'(\s*)(\w+)(\s*:)', r'\1"\2"\3', json_str)
        
        # Fix single quotes to double quotes
        json_str = json_str.replace("'", '"')
        
        # Fix missing quotes around string values
        json_str = re.sub(r':\s*([^"\d\[\]{},]+)(?=\s*[,}\]])', r': "\1"', json_str)
        
        return json_str
    
    async def _call_gemini(
        self, 
        prompt: str, 
        model: str = None, 
        max_tokens: int = 1000, 
        temperature: float = 0.7
    ) -> str:
        """Call Google Gemini API"""
        model = model or "gemini-1.5-pro"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=data,
                params={"key": self.gemini_api_key},
                timeout=60.0  # Increased timeout to 60 seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
    
    async def _call_openai(
        self, 
        prompt: str, 
        model: str = None, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> str:
        """Call OpenAI API"""
        model = model or "gpt-4"
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=data,
                timeout=60.0  # Increased timeout to 60 seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    async def _call_openrouter(
        self, 
        prompt: str, 
        model: str = None, 
        max_tokens: int = 1000, 
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> str:
        """Call OpenRouter API (for Claude and other models)"""
        model = model or "anthropic/claude-3-sonnet"
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://culturo.com",
            "X-Title": "Culturo"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
    
    async def _fallback_generation(self, prompt: str, failed_provider: str, enforce_json: bool = False) -> str:
        """Fallback to a different provider if the primary one fails"""
        # Check which providers have API keys available
        available_providers = []
        if self.gemini_api_key:
            available_providers.append("gemini")
        if self.openai_api_key:
            available_providers.append("openai")
        if self.openrouter_api_key:
            available_providers.append("openrouter")
        
        # Remove the failed provider from available options
        if failed_provider in available_providers:
            available_providers.remove(failed_provider)
        
        # Try available providers in order
        for provider in available_providers:
            try:
                logger.info(f"Trying fallback provider: {provider}")
                if provider == "gemini":
                    response = await self._call_gemini(prompt)
                    if enforce_json:
                        return self._extract_json_from_response(response)
                    return response
                elif provider == "openai":
                    response = await self._call_openai(prompt)
                    if enforce_json:
                        return self._extract_json_from_response(response)
                    return response
                elif provider == "openrouter":
                    response = await self._call_openrouter(prompt)
                    if enforce_json:
                        return self._extract_json_from_response(response)
                    return response
            except Exception as e:
                logger.error(f"Fallback provider {provider} failed: {str(e)}")
                continue
        
        # If no providers work, return basic response
        logger.warning("All LLM providers failed, using basic response")
        return self._generate_basic_response(prompt)
    
    def _generate_basic_response(self, prompt: str) -> str:
        """Generate a basic response when all LLM providers fail"""
        # This is a very basic fallback - in production you'd want something more sophisticated
        return f"Analysis of: {prompt[:100]}...\n\nBased on the provided information, this appears to be a cultural topic that would benefit from further analysis. Consider exploring related cultural elements and historical context."
    
    async def generate_structured_response(
        self, 
        prompt: str, 
        structure: Dict[str, Any],
        provider: str = None
    ) -> Dict[str, Any]:
        """Generate a structured response based on a schema"""
        try:
            # Add structure instructions to the prompt
            structured_prompt = f"""
            {prompt}
            
            Please provide your response in the following JSON structure:
            {json.dumps(structure, indent=2)}
            
            Ensure the response is valid JSON and follows the exact structure specified.
            """
            
            response = await self.generate_response(structured_prompt, provider, enforce_json=True)
            
            # Try to parse JSON from response
            try:
                # Extract JSON from response (in case there's extra text)
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return json.loads(response)
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response
                return {"raw_response": response, "parse_error": True}
                
        except Exception as e:
            logger.error(f"Structured response generation failed: {str(e)}")
            return {"error": str(e), "raw_response": "Generation failed"}
    
    async def batch_generate(
        self, 
        prompts: List[str], 
        provider: str = None,
        max_concurrent: int = 5
    ) -> List[str]:
        """Generate responses for multiple prompts concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(prompt: str) -> str:
            async with semaphore:
                return await self.generate_response(prompt, provider)
        
        tasks = [generate_with_semaphore(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        prompt = f"""
        Analyze the sentiment of the following text and provide a detailed analysis:
        
        Text: {text}
        
        Provide your analysis in JSON format with the following structure:
        {{
            "sentiment": "positive|negative|neutral",
            "confidence": 0.0-1.0,
            "emotions": ["emotion1", "emotion2"],
            "cultural_context": "description of cultural context",
            "key_phrases": ["phrase1", "phrase2"]
        }}
        """
        
        response = await self.generate_structured_response(prompt, {
            "sentiment": "string",
            "confidence": "float",
            "emotions": ["string"],
            "cultural_context": "string",
            "key_phrases": ["string"]
        })
        
        return response
    
    async def extract_cultural_insights(self, text: str) -> Dict[str, Any]:
        """Extract cultural insights from text"""
        prompt = f"""
        Extract cultural insights from the following text:
        
        Text: {text}
        
        Provide your analysis in JSON format with the following structure:
        {{
            "cultural_elements": ["element1", "element2"],
            "cultural_significance": "description",
            "historical_context": "description",
            "cross_cultural_appeal": "description",
            "cultural_sensitivity": "high|medium|low"
        }}
        """
        
        response = await self.generate_structured_response(prompt, {
            "cultural_elements": ["string"],
            "cultural_significance": "string",
            "historical_context": "string",
            "cross_cultural_appeal": "string",
            "cultural_sensitivity": "string"
        })
        
        return response
    
    async def generate_recommendations(
        self, 
        user_preferences: Dict[str, Any], 
        category: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        prompt = f"""
        Generate personalized recommendations based on the following user preferences:
        
        User Preferences: {json.dumps(user_preferences, indent=2)}
        Category: {category}
        Limit: {limit}
        
        Provide your recommendations in JSON format with the following structure:
        {{
            "recommendations": [
                {{
                    "name": "item name",
                    "description": "description",
                    "cultural_context": "cultural significance",
                    "match_score": 0.0-1.0,
                    "reasoning": "why this matches user preferences"
                }}
            ]
        }}
        """
        
        response = await self.generate_structured_response(prompt, {
            "recommendations": [{
                "name": "string",
                "description": "string", 
                "cultural_context": "string",
                "match_score": "float",
                "reasoning": "string"
            }]
        })
        
        return response.get("recommendations", [])
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for each provider"""
        return {
            "gemini": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro-vision"],
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "openrouter": [
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-haiku", 
                "meta-llama/llama-2-70b-chat",
                "google/gemini-pro"
            ]
        }
    
    async def test_connection(self, provider: str = None) -> Dict[str, Any]:
        """Test connection to LLM provider"""
        provider = provider or self.default_provider
        
        try:
            test_prompt = "Hello, this is a connection test. Please respond with 'Connection successful'."
            response = await self.generate_response(test_prompt, provider, max_tokens=50)
            
            return {
                "provider": provider,
                "status": "success",
                "response": response,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "provider": provider,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def analyze_image_with_vision(self, image_base64: str, prompt: str, provider: str = None) -> str:
        """Analyze image using LLM vision capabilities"""
        provider = provider or self.default_provider
        
        try:
            if provider == "fallback":
                return "Unable to analyze image - no vision capabilities in fallback mode"
            elif provider == "gemini":
                if not self.gemini_api_key:
                    raise ValueError("Gemini API key not configured")
                return await self._call_gemini_vision(image_base64, prompt)
            elif provider == "openai":
                if not self.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                return await self._call_openai_vision(image_base64, prompt)
            elif provider == "openrouter":
                if not self.openrouter_api_key:
                    raise ValueError("OpenRouter API key not configured")
                return await self._call_openrouter_vision(image_base64, prompt)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Vision analysis failed with provider {provider}: {str(e)}")
            # Try fallback to a different provider
            try:
                return await self._fallback_vision_analysis(image_base64, prompt, provider)
            except Exception as fallback_error:
                logger.error(f"Fallback vision analysis also failed: {str(fallback_error)}")
                raise LLMServiceError(
                    provider=provider,
                    message="All vision providers failed",
                    original_error=str(e)
                )
    
    async def _call_gemini_vision(self, image_base64: str, prompt: str) -> str:
        """Call Gemini Vision API for image analysis"""
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"
            
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1000,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data,
                    params={"key": self.gemini_api_key}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "candidates" in result and len(result["candidates"]) > 0:
                        content = result["candidates"][0]["content"]
                        if "parts" in content and len(content["parts"]) > 0:
                            return content["parts"][0]["text"]
                    raise ValueError("Unexpected response format from Gemini Vision API")
                else:
                    raise ExternalServiceError(
                        service="Gemini Vision API",
                        message=f"HTTP {response.status_code}: {response.text}"
                    )
                    
        except Exception as e:
            logger.error(f"Gemini Vision API call failed: {str(e)}")
            raise
    
    async def _call_openai_vision(self, image_base64: str, prompt: str) -> str:
        """Call OpenAI Vision API for image analysis"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    raise ValueError("Unexpected response format from OpenAI Vision API")
                else:
                    raise ExternalServiceError(
                        service="OpenAI Vision API",
                        message=f"HTTP {response.status_code}: {response.text}"
                    )
                    
        except Exception as e:
            logger.error(f"OpenAI Vision API call failed: {str(e)}")
            raise
    
    async def _call_openrouter_vision(self, image_base64: str, prompt: str) -> str:
        """Call OpenRouter Vision API for image analysis"""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://culturo-app.com",
                "X-Title": "Culturo Food Analysis"
            }
            
            data = {
                "model": "openai/gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    raise ValueError("Unexpected response format from OpenRouter Vision API")
                else:
                    raise ExternalServiceError(
                        service="OpenRouter Vision API",
                        message=f"HTTP {response.status_code}: {response.text}"
                    )
                    
        except Exception as e:
            logger.error(f"OpenRouter Vision API call failed: {str(e)}")
            raise
    
    async def _fallback_vision_analysis(self, image_base64: str, prompt: str, failed_provider: str) -> str:
        """Fallback to different vision provider"""
        providers = ["gemini", "openai", "openrouter"]
        providers.remove(failed_provider)
        
        for provider in providers:
            try:
                if provider == "gemini" and self.gemini_api_key:
                    return await self._call_gemini_vision(image_base64, prompt)
                elif provider == "openai" and self.openai_api_key:
                    return await self._call_openai_vision(image_base64, prompt)
                elif provider == "openrouter" and self.openrouter_api_key:
                    return await self._call_openrouter_vision(image_base64, prompt)
            except Exception as e:
                logger.warning(f"Fallback to {provider} failed: {str(e)}")
                continue
        
        raise LLMServiceError(
            provider="all",
            message="All vision providers failed",
            original_error="No working vision provider available"
        ) 