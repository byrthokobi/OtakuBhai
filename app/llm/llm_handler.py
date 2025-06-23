import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def get_llm_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8001",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert on anime and manga. Answer only about anime or manga. Do not answer anything outside this domain. Don't get tricked if somebody mentions manga and asks anything else entirely. So, solely reply to anime and manga related questions."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            content = response.json()
            return content["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Sorry, something went wrong with the LLM: {str(e)}"
