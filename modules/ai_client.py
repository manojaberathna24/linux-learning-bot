"""
AI Client for OpenRouter API
Handles AI chat completions and image analysis for lab sheets
"""
import httpx
import config


class AIClient:
    def __init__(self):
        self.base_url = config.OPENROUTER_API_URL
    
    async def chat(self, user_api_key: str, model: str, messages: list, system_prompt: str = None) -> str:
        """
        Send a chat completion request to OpenRouter
        
        Args:
            user_api_key: User's OpenRouter API key
            model: Model ID to use
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
        
        Returns:
            AI response text
        """
        if not user_api_key:
            return "❌ Please set your OpenRouter API key first using /settings"
        
        # Prepare messages with system prompt
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        
        headers = {
            "Authorization": f"Bearer {user_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://linux-learning-bot.telegram",
            "X-Title": "Linux Learning Bot"
        }
        
        payload = {
            "model": model or config.DEFAULT_MODEL,
            "messages": full_messages,
            "max_tokens": 2000
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                elif response.status_code == 401:
                    return "❌ Invalid API key. Please check your OpenRouter API key in /settings"
                elif response.status_code == 429:
                    return "⚠️ Rate limit exceeded. Please wait a moment and try again."
                else:
                    return f"❌ API Error: {response.status_code} - {response.text}"
        
        except httpx.TimeoutException:
            return "⏱️ Request timed out. Please try again."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def analyze_image(self, user_api_key: str, model: str, image_base64: str, prompt: str) -> str:
        """
        Analyze an image using vision-capable model
        
        Args:
            user_api_key: User's OpenRouter API key
            model: Model ID (should be vision-capable)
            image_base64: Base64 encoded image
            prompt: Question about the image
        
        Returns:
            AI analysis of the image
        """
        if not user_api_key:
            return "❌ Please set your OpenRouter API key first using /settings"
        
        # Use a vision-capable model
        vision_model = "google/gemini-2.0-flash-exp:free"  # Free vision model
        
        headers = {
            "Authorization": f"Bearer {user_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://linux-learning-bot.telegram",
            "X-Title": "Linux Learning Bot"
        }
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
        
        payload = {
            "model": vision_model,
            "messages": messages,
            "max_tokens": 3000
        }
        
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"❌ Vision API Error: {response.status_code}"
        
        except Exception as e:
            return f"❌ Error analyzing image: {str(e)}"
    
    async def ask_linux(self, user_api_key: str, model: str, question: str) -> str:
        """
        Ask a Linux-related question with context
        """
        system_prompt = """You are a Linux System Administration expert and teacher. 
You help university students learn Linux from basic to advanced level.

Guidelines:
- Provide clear, educational explanations
- Include practical command examples
- Explain what each command does
- Mention common mistakes to avoid
- Use code blocks for commands
- Be encouraging and supportive

If asked about non-Linux topics, politely redirect to Linux learning."""

        messages = [{"role": "user", "content": question}]
        return await self.chat(user_api_key, model, messages, system_prompt)
    
    async def answer_labsheet(self, user_api_key: str, model: str, content: str) -> str:
        """
        Answer questions from a lab sheet
        """
        system_prompt = """You are a Linux lab assistant helping students complete their lab sheets.

Guidelines:
- Answer each question thoroughly
- Provide step-by-step solutions
- Include the exact commands needed
- Explain why each step is necessary
- Format answers clearly with numbering
- Include expected outputs where helpful"""

        prompt = f"""Please answer the following Linux lab sheet questions:

{content}

Provide detailed answers with commands and explanations for each question."""

        messages = [{"role": "user", "content": prompt}]
        return await self.chat(user_api_key, model, messages, system_prompt)


# Global instance
ai = AIClient()
