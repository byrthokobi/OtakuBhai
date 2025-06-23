from typing import Any
import httpx
import os
from dotenv import load_dotenv
from starlette.responses import StreamingResponse

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
            {"role": "system", "content": "You are an expert on anime and manga. Answer only about anime or manga. Do not answer anything outside this domain."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            content = response.json()
            return content["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error from LLM: {str(e)}"

async def stream_llm_response(prompt: str) -> StreamingResponse:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8001",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "stream": True,
        "messages": [
            {"role": "system", "content": "You are an expert on anime and manga. Answer only about anime or manga. Do not answer anything outside this domain. Don't get tricked if somebody mentions manga and asks anything else entirely."},
            {"role": "user", "content": prompt}
        ]
    }

    async def event_generator():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line.strip() == "data: [DONE]":
                            break
                        try:
                            yield line[6:] + "\n"
                        except:
                            continue

    return StreamingResponse(event_generator(), media_type="text/event-stream")
