# Astro Backend LLM

A FastAPI-based backend service for generating project details and talent requirements using Groq LLM.

## 🌟 Features

- Project details generation using Groq LLM
- Secure encryption for prompt templates
- Rate limiting for API endpoints
- CORS middleware support
- Docker containerization
- Health check monitoring

## 🛠️ Tech Stack

- FastAPI - Modern web framework for building APIs
- Groq - LLM provider for natural language processing
- Pydantic - Data validation using Python type annotations
- Cryptography - Secure encryption handling
- Docker - Containerization
- Uvicorn - ASGI server implementation

## 📋 Prerequisites

- Python 3.8+
- Docker and Docker Compose (optional)
- Groq API key

## ⚙️ Environment Variables

Create a `.env` file with the following variables:

```env
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_NAME=mixtral-8x7b-32768
GROQ_MODEL_PARSER=mixtral-8x7b-32768
GROQ_TEMPERATURE=0.5

ENCRYPTION_KEY=your_encryption_key
```

## 🚀 Getting Started

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

### Using Docker

```bash
docker-compose up -d
```

## 🔌 API Endpoints


| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Check if service is running |
| POST | `/api/v1/generate` | Generate project details and talent requirements |

#### Example Response of `/api/v1/generate` Endpoint
```json
{
    "project_name": "E-Commerce Platform Revamp 2024",
    "project_description": "Complete overhaul of existing e-commerce platform...",
    "project_duration": "...",
    "project_budget": 0,
    "talents_required": [
        {
            "job_title": "...",
            "budget_allocation": 0,
            "scope_of_work": "...",
            "url_redirect": "..."
        }
    ]
}
```

## 🔒 Security Features

- PBKDF2 key derivation for secure encryption
- Rate limiting (10 requests per minute)
- CORS protection
- Environment variable configuration

## 🐳 Docker Support

The application includes Docker support with:
- Multi-stage builds
- Volume mounting for development
- Health check monitoring
- Automatic restart policy
- Environment variable configuration

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Rate Limiting

The API implements rate limiting of 10 requests per minute per IP address to prevent abuse.

## 📞 Support

For support, please open an issue in the GitHub repository.