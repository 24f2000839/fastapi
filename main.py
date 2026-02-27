from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import json

app = FastAPI()

# 🔹 Use OpenRouter instead of OpenAI
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

# -------------------------
# Request Model
# -------------------------
class CommentRequest(BaseModel):
    comment: str

# -------------------------
# Response Model
# -------------------------
class SentimentResponse(BaseModel):
    sentiment: str
    rating: int

# -------------------------
# POST Endpoint
# -------------------------
@app.post("/comment", response_model=SentimentResponse)
def analyze_comment(request: CommentRequest):
    try:

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",   # or openai/gpt-4.1-mini if available
            messages=[
                {
                    "role": "system",
                    "content": """You are a sentiment analysis API.
Return ONLY valid JSON in this exact format:
{
  "sentiment": "positive|negative|neutral",
  "rating": 1-5
}
Do not add any extra text."""
                },
                {
                    "role": "user",
                    "content": request.comment
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON safely
        try:
            result = json.loads(content)
        except:
            raise HTTPException(status_code=500, detail="Model did not return valid JSON")

        # Validate manually
        if result["sentiment"] not in ["positive", "negative", "neutral"]:
            raise HTTPException(status_code=500, detail="Invalid sentiment value")

        if not (1 <= int(result["rating"]) <= 5):
            raise HTTPException(status_code=500, detail="Invalid rating value")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
