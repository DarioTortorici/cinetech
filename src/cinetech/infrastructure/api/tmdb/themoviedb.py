import os
from typing import Any

import requests

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


class TMDbClient:
    """
    Client for interacting with TheMovieDB (TMDb) REST API.

    Provides methods to search for movies, fetch details, get popular/top-rated movies, genres, and posters.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize TMDbClient.

        Args:
            api_key (str | None): TMDb API key. If None, uses environment variable TMDB_API_KEY.

        Raises:
            ValueError: If API key is not set.
        """
        self.api_key = api_key or TMDB_API_KEY
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not set in environment or passed to TMDbClient.")

    def search_movie(self, query: str, page: int = 1) -> list[dict[str, Any]]:
        """
        Search for movies by name.

        Args:
            query (str): Movie name to search for.
            page (int): Page number for results.

        Returns:
            list: List of movie dictionaries.
        """
        url = f"{TMDB_BASE_URL}/search/movie"
        params = {"api_key": self.api_key, "query": query, "page": page, "language": "en-US"}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])

    def get_movie_details(self, movie_id: int) -> dict[str, Any]:
        """
        Get details for a specific movie by its TMDb ID.

        Args:
            movie_id (int): TMDb movie ID.

        Returns:
            dict: Movie details.
        """
        url = f"{TMDB_BASE_URL}/movie/{movie_id}"
        params = {"api_key": self.api_key, "language": "en-US"}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_movie_credits(self, movie_id: int) -> dict[str, Any]:
        """
        Get credits (cast and director) for a specific movie by its TMDb ID.

        Args:
            movie_id (int): TMDb movie ID.
        Returns:
            dict: Movie credits.
        """
        url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
        params = {"api_key": self.api_key, "language": "en-US"}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        # Extract top 5 cast members
        cast = data.get("cast", [])[:5]
        # Extract director(s) from crew
        directors = [member for member in data.get("crew", []) if member.get("job") == "Director"]
        return {"cast": cast, "director": directors}

    def get_popular(self, page: int = 1) -> list[dict[str, Any]]:
        """
        Get popular movies.

        Args:
            page (int): Page number for results.

        Returns:
            list: List of popular movie dictionaries.
        """
        url = f"{TMDB_BASE_URL}/movie/popular"
        params = {"api_key": self.api_key, "page": page, "language": "en-US"}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])

    def get_top_rated(self, page: int = 1) -> list[dict[str, Any]]:
        """
        Get top-rated movies.

        Args:
            page (int): Page number for results.

        Returns:
            list: List of top-rated movie dictionaries.
        """
        url = f"{TMDB_BASE_URL}/movie/top_rated"
        params = {"api_key": self.api_key, "page": page, "language": "en-US"}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])

    def get_genres(self) -> list[dict[str, Any]]:
        """
        Get list of movie genres.

        Returns:
            list: List of genre dictionaries.
        """
        url = f"{TMDB_BASE_URL}/genre/movie/list"
        params = {"api_key": self.api_key, "language": "en-US"}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("genres", [])

    def get_movie_poster(self, movie_id: int) -> dict[str, Any]:
        """
        Retrieve the poster for a specific movie by its TMDb ID, filtering for English posters.

        Args:
            movie_id (int): TMDb movie ID.

        Returns:
            str : File path of the poster if found, else None.
        """
        url = f"{TMDB_BASE_URL}/movie/{movie_id}/images"
        params = {"api_key": self.api_key, "include_image_language": "en,null"}
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        posters = data.get("posters", [])
        for poster in posters:
            if (
                poster.get("aspect_ratio") == 0.667
                and poster.get("height") == 3000
                and poster.get("iso_639_1") == "en"
                and poster.get("width") == 2000
            ):
                return poster.get("file_path")
        return None
