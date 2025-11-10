from fastapi import FastAPI
from fastapi.testclient import TestClient

# Minimal FastAPI app for endpoint testing
app = FastAPI()


@app.get("/")
async def read_main():
    """
    Root endpoint for test FastAPI app.
    Returns a hello world message.
    """
    return {"msg": "Hello World"}


client = TestClient(app)


def test_read_main():
    """
    Test the root endpoint returns correct status and message.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_fetch_movies_from_tmdb():
    """
    Test fetch_movies_from_tmdb returns a list of movies with required fields.
    Skips if TMDB_API_KEY is not set.
    """
    import os

    from cinetech.application.ingestion_service import ingestion_service

    tmdb_api_key = os.getenv("TMDB_API_KEY", "")
    if not tmdb_api_key:
        import pytest

        pytest.skip("TMDB_API_KEY not set")
    movies = ingestion_service.fetch_movies_from_tmdb(tmdb_api_key, num_movies=2)
    assert isinstance(movies, list)
    assert len(movies) == 2
    for movie in movies:
        assert "title" in movie
        assert "overview" in movie
        assert "genres" in movie
        assert "cast" in movie
        assert "director" in movie
        assert "year" in movie
        assert "rating" in movie
