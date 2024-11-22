import os
from fastapi import APIRouter
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, List
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler


# Environment Configuration
# =======================================================================================

load_dotenv()
class Config:

    SERVER_HOST: str = os.getenv("SERVER_HOST")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT"))
    SERVER_DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE"))

# =======================================================================================


# LLM Agent PoC
# =======================================================================================

class AstroAgent:
    """
    # NOTE: Research kan dulu le.
    Implement ReAct Agent to Generate Project Detail Information and Parsing the Information as Structured JSON Output using Instructor.
    """
    pass

# =======================================================================================

# Instance Configuration
# =======================================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = ...
    yield

app = FastAPI(
    title="astro-backend-llm",
    description="Backend LLM for Astro",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

router = APIRouter(prefix="/api/v1", tags=["llm"])

# =======================================================================================


# Pydantic Model
# =======================================================================================

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="User prompt to generate project detail information.")

class DefaultResponse(BaseModel):
    message: str = "success"

class TalentRequired(BaseModel):
    job_title: str
    budget_allocation: float
    scope_of_word: str
    url_redirect: str

class GenerateResponse(BaseModel):
    brief_project_description: str
    talent_required: List[TalentRequired]

# =======================================================================================


# Endpoints Route
# =======================================================================================

@router.get("/", response_model=DefaultResponse)
async def root():
    return DefaultResponse(message="service is running...")

@router.get("/health", response_model=DefaultResponse)
async def health():
    return DefaultResponse()

@router.post("/generate")
@limiter.limit("10/minute")
async def generate(request: GenerateRequest):
    return ...

# =======================================================================================


# Run Server
# =======================================================================================

if __name__ == "__main__":

    import uvicorn
    if Config.SERVER_DEBUG:
        uvicorn.run("app:app", host=Config.SERVER_HOST, port=Config.SERVER_PORT, reload=True)
    else:
        uvicorn.run("app:app", host=Config.SERVER_HOST, port=Config.SERVER_PORT)

# =======================================================================================