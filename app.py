import os
import base64
import instructor
from groq import Groq
from typing import List, Dict
from fastapi import APIRouter
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from cryptography.fernet import Fernet
from contextlib import asynccontextmanager
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from cryptography.hazmat.primitives import hashes
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Environment Configuration
# =======================================================================================

load_dotenv()
class Config:

    SERVER_HOST: str = os.getenv("SERVER_HOST")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT"))
    SERVER_DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME")
    GROQ_MODEL_PARSER: str = os.getenv("GROQ_MODEL_PARSER")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE"))

    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY")

# =======================================================================================


# Encryption Configuration
# =======================================================================================

class ExtractSecret:

    def __init__(self, filename: str = "enc_prompt.txt"):

        self.filename = filename
        self.key = self._key_gen(Config.ENCRYPTION_KEY)

    def _key_gen(self, salt_key: str) -> bytes:
        """
        Generate encryption key from salt key
        
        Args:
            salt_key (str): Salt key used for key derivation
            
        Returns:
            bytes: Generated encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_key.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"ENCRYPTION_KEY"))
        return key

    def decrypt_file(self,) -> str:
        """
        Decrypt file content using Fernet decryption with custom salt key
        
        Returns:
            str: Decrypted file content as string
        """
        f = Fernet(self.key)
        with open(self.filename, 'rb') as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode()

# =======================================================================================

# LLM Agent PoC
# =======================================================================================

class ParserTalentRequired(BaseModel):
    job_title: str = Field(
        ...,
        description="Specific job title/role for the position",
        min_length=3,
        max_length=100,
        examples=["Senior Frontend Developer", "UI/UX Designer"]
    )
    budget_allocation: float = Field(
        ...,
        description="Allocated budget for this specific role in Rupiah Range",
        gt=0,
        examples=[1000000, 25000000]
    )
    scope_of_work: str = Field(
        ...,
        description="Detailed description of responsibilities and deliverables",
        min_length=10,
        max_length=1500,
        examples=["Develop and maintain frontend features using React.js, implement responsive design"]
    )
    url_redirect: str = Field(
        ...,
        description="URL path for the job detail page",
        examples=["https://www.upwork.com/nx/search/talent/?nbs=1&q=AI%20engineer"]
    )

class ParserProjectDetails(BaseModel):
    project_name: str = Field(
        ...,
        description="Name of the project",
        min_length=5,
        max_length=200,
        examples=["E-Commerce Platform Revamp 2024"]
    )
    project_description: str = Field(
        ...,
        description="Comprehensive project description including objectives and expected outcomes",
        min_length=50,
        max_length=1000
    )
    project_duration: str = Field(
        ...,
        description="Expected duration of the project",
        examples=["3 months", "6 weeks", "1 year"]
    )
    project_budget: float = Field(
        ...,
        description="Total project budget allocation",
        gt=0,
        examples=[10_000_000, 100_000_000]
    )
    talents_required: List[ParserTalentRequired] = Field(
        ...,
        description="List of required talents/roles for the project",
        min_items=1
    )

class AstroAgent:

    def __init__(self):
        
        self.llm = Groq(api_key=Config.GROQ_API_KEY)
        self.client_inst = instructor.from_groq(self.llm)
        self.inst_prompt = ExtractSecret().decrypt_file()

    def generate_project_details(self, prompt: str) -> Dict:
        """
        Generate project details based on the provided prompt using LLM.
        
        Args:
            prompt (str): User input describing the project requirements and needs
            
        Returns:
            Dict: Project details in dictionary format
        """
        project_details = self.llm.chat.completions.create(
            model=Config.GROQ_MODEL_NAME,
            temperature=Config.GROQ_TEMPERATURE,
            messages=[{"role": "user", "content": self.inst_prompt.format(prompt=prompt)}]
        ).choices[0].message.content
        result_parser = self.client_inst.completions.create(
            model=Config.GROQ_MODEL_PARSER,
            response_model=ParserProjectDetails,
            messages=[{"role": "user", "content": f"Extract: {project_details}"}]
        )
        result = result_parser.model_dump()
        return result


# =======================================================================================

# Instance Configuration
# =======================================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = AstroAgent()
    yield

app = FastAPI(
    title="astro-backend-llm",
    description="Backend LLM for Astro",
    version="1.0.0",
    lifespan=lifespan
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
    scope_of_work: str
    url_redirect: str

class GenerateResponse(BaseModel):
    project_name: str
    project_description: str
    project_duration: str
    project_budget: float
    talents_required: List[TalentRequired]

# =======================================================================================


# Endpoints Route
# =======================================================================================

@app.get("/", response_model=DefaultResponse, include_in_schema=False)
async def root():
    return DefaultResponse(message="service is running...")

@router.get("/health", response_model=DefaultResponse)
async def health():
    return DefaultResponse()

@router.post("/generate", response_model=GenerateResponse)
@limiter.limit("10/minute")
async def generate(request: Request, request_body: GenerateRequest):
    return app.state.agent.generate_project_details(request_body.prompt)

app.include_router(router)

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