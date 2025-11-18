
# Cinetech

![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)
[![Groq Llama](https://img.shields.io/badge/Groq-Llama-orange?style=flat&colorA=orange&colorB=blue)](https://groq.com/)
![ChromaDB](https://img.shields.io/badge/ChromaDB-008D8D?style=flat&logo=chroma)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-034B75?style=flat&logo=llama-index&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-59C756?style=flat&logo=langchain&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit)
![Ruff](https://img.shields.io/badge/Ruff-000000?style=flat&logo=ruff&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)
![Coverage](https://img.shields.io/badge/coverage-61%25-orange)

---

**Cinetech** is a movie recommendation platform that leverages conversational AI and semantic search to deliver personalized film suggestions. Users can interact with the Cinetech Agent via a chat interface, search for movies, and manage their favorite films.

## Features

- Conversational movie recommendation agent
- Semantic search for movies using ChromaDB and LlamaIndex
- TMDb API integration for movie metadata and posters
- Persistent user context and favorites
- FastAPI backend endpoints
- Streamlit web app
- Modular, extensible architecture for agents, tools, and prompts
- Logging and monitoring
- Unit tests

---

## Installation

Make sure you have Python 3.12 installed.

### 1. Clone the repository

```powershell
git clone https://github.com/DarioTortorici/cinetech.git
cd cinetech
```

### 2. Set Virtual envirorment

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```powershell
pip install uv
uv sync
```

### 3. Install dependencies

The dependancies will be already installed in the virtual envirorment.
The envirorment can be activated.

```powershell
/.venv/scripts/activate
```

### 4. Envirorment variables

Create .env file and popolate it with:

1. Groq API key

## Environment Variables

Create a `.env` file in the project root with the following content:

```env
GROQ_API_KEY=your_groq_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here
HF_API_KEY=your_hf_api_key_here
```

- `GROQ_API_KEY`: Your Groq API key for conversational AI features.
- `TMDB_API_KEY`: Your TMDb API key for movie metadata and posters.
- `HF_API_KEY`: Your Hugging Face API key for embedding and query search in the vector database.

Keep your API keys secure and do not share your `.env` file publicly.

---

## Usage

### Streamlit

Access the chat interface at [http://localhost:8501](http://localhost:8501) after starting Streamlit.
⚠️ WARNING: The first usage of streamlit will need be delayed due to extra dependencies integration.
You can safely skip the email insertion.

```powershell
streamlit run streamlit_app.py
```

### API

The backend API is available at [http://localhost:8000](http://localhost:8000) after starting FastAPI.

```powershell
cd src/cinetech/infrastructure/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Test

These tests cover 60% of the code. This can be verified by running the pytest and coverage packages.

```powershell
coverage run -m pytest
coverage report

```

---

## Project Structure

```
cinetech/
├── src/
│   └── cinetech/
│       ├── application/      # Chat and ingestion services
│       ├── domain/           # Agent logic, prompts, tools, memory
│       ├── infrastructure/   # API, database, monitoring, TMDb client
│       └── ...
├── tests/                    # Tests
├── streamlit_app.py          # Streamlit web app
├── pyproject.toml            # Project metadata
└── README.md                 # Project documentation
```

---

## Credits

This product uses the TMDb API but is not endorsed or certified by TMDb. The TMDb API is used for personal, non-commercial purposes only. See [TMDb terms of use](https://www.themoviedb.org/documentation/api/terms-of-use).

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [agent-api-cookiecutter](https://github.com/neural-maze/agent-api-cookiecutter) project template.
