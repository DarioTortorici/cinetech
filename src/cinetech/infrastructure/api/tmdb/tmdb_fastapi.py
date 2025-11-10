import os

from fastapi import APIRouter, HTTPException, Query

from cinetech.infrastructure.api.tmdb.themoviedb import TMDbClient

router = APIRouter()

# Singleton TMDbClient instance
tmdb_client = None
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")


def get_tmdb():
    """
    Retrieve a singleton TMDbClient instance.

    Returns:
        TMDbClient: The TMDb API client.
    """
    global tmdb_client
    if tmdb_client is None:
        tmdb_client = TMDbClient(api_key=TMDB_API_KEY)
    return tmdb_client


@router.get("/search")
async def tmdb_search(query: str = Query(..., description="Movie search query"), page: int = Query(1, ge=1)):
    """
    Search for movies on TheMovieDB.

    Args:
        query (str): Movie search query.
        page (int): Page number for results.

    Returns:
        dict: Search results.
    """
    tmdb_client = get_tmdb()
    try:
        results = tmdb_client.search_movie(query, page=page)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/details/{movie_id}")
async def tmdb_details(movie_id: int):
    """
    Get details for a movie from TheMovieDB.

    Args:
        movie_id (int): TMDb movie ID.

    Returns:
        dict: Movie details.
    """
    tmdb_client = get_tmdb()
    try:
        details = tmdb_client.get_movie_details(movie_id)
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/top_rated")
async def tmdb_top_rated(page: int = Query(1, ge=1)):
    """
    Get top-rated movies from TheMovieDB.

    Args:
        page (int): Page number for results.

    Returns:
        dict: Top-rated movie results.
    """
    tmdb_client = get_tmdb()
    try:
        results = tmdb_client.get_top_rated(page=page)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/popular")
async def tmdb_popular(page: int = Query(1, ge=1)):
    """
    Get popular movies from TheMovieDB.

    Args:
        page (int): Page number for results.

    Returns:
        dict: Popular movie results.
    """
    tmdb_client = get_tmdb()
    try:
        results = tmdb_client.get_popular(page=page)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/genres")
async def tmdb_genres():
    """
    Get list of genres from TheMovieDB.

    Returns:
        dict: List of genres.
    """
    tmdb_client = get_tmdb()
    try:
        genres = tmdb_client.get_genres()
        return {"genres": genres}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/images/{movie_id}")
async def tmdb_movie_images(movie_id: int):
    """
    Get images (posters, backdrops, etc.) for a movie from TheMovieDB.

    Args:
        movie_id (int): TMDb movie ID.

    Returns:
        str | None: File path of the poster if found, else None.
    """
    tmdb_client = get_tmdb()
    try:
        images = tmdb_client.get_movie_poster(movie_id)
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
