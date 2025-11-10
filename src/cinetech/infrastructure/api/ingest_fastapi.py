import os

from fastapi import APIRouter, Query
from pydantic import BaseModel

from cinetech.application.ingestion_service.ingestion_service import (
    fetch_movies_from_tmdb,
    ingest_movies,
    search_movies,
)

# Router for ingestion endpoints
router = APIRouter()

# API key and default number of movies to ingest
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
NUM_MOVIES = 100


class MovieSearchResult(BaseModel):
    """
    Pydantic model for movie search results.
    Used as response model for human-friendly semantic search endpoint.
    """

    title: str
    genres: str
    director: str
    year: str
    score: float
    description: str


class IngestRequest(BaseModel):
    """
    Pydantic model for ingest request payload.
    Used as input for the ingest endpoint.
    """

    num_movies: int | None = NUM_MOVIES


@router.post("/ingest")
def ingest_movies_endpoint(request: IngestRequest):
    """
    Ingest movies from TMDb into the vector database.

    Args:
        request (IngestRequest): Request payload with number of movies to ingest.

    Returns:
        dict: Message with number of movies ingested.
    """
    movies_data = fetch_movies_from_tmdb(TMDB_API_KEY, request.num_movies)
    ingest_movies(movies_data)
    return {"message": f"Ingested {len(movies_data)} movies."}


@router.get("/search", response_model=list[MovieSearchResult])
def search_movies_endpoint(query: str = Query(..., description="Search query for movies"), top_k: int = 5):
    """
    Perform a human-friendly semantic search for movies.

    Args:
        query (str): Search query for movies.
        top_k (int): Number of top results to return.

    Returns:
        list[MovieSearchResult]: List of movie search results.
    """
    results = search_movies(query, top_k)
    return results
