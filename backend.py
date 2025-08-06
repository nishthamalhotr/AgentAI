from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq
import os

# Load environment variables from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Valid GROQ_API_KEY is missing in .env file.")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize FastAPI
app = FastAPI(title="AI Tutor API")

# CORS settings (for frontend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chat history
chat_history = []

# Request models
class TutorRequest(BaseModel):
    subject: str
    level: str
    style: str
    language: str
    question: str

class FollowupRequest(BaseModel):
    question: str

@app.post("/tutor")
def create_tutor_request(request: TutorRequest):
    """Handles the first tutor question using LLaMA."""
    global chat_history
    try:
        prompt = f"""
        You are an AI tutor expert in {request.subject} at {request.level} level 
        with a {request.style} learning style in {request.language}.

        Question: {request.question}

        Provide a clear, structured explanation with examples.
        """

        # Call LLaMA via Groq
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful tutor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        answer = response.choices[0].message.content
        chat_history = [(request.question, answer)]

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLaMA error: {str(e)}")


@app.post("/ask")
def ask_followup(request: FollowupRequest):
    """Handles follow-up questions with LLaMA."""
    global chat_history
    if not chat_history:
        raise HTTPException(
            status_code=400,
            detail="No active conversation. Please start with /tutor first."
        )

    try:
        # Build conversation history
        messages = [{"role": "system", "content": "You are a helpful tutor."}]
        for q, a in chat_history:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})

        # Add new question
        messages.append({"role": "user", "content": request.question})

        # Call LLaMA via Groq
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.2
        )

        answer = response.choices[0].message.content
        chat_history.append((request.question, answer))

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLaMA error: {str(e)}")
