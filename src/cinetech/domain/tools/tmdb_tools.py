import json
import os

from langchain.tools import BaseTool

from cinetech.infrastructure.api.tmdb.themoviedb import TMDbClient
from cinetech.infrastructure.monitoring.logger import Logger

logger = Logger.get_logger("cinetech.tmdb_tools")

# Path to favourites file
FAVOURITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "infrastructure", "db", "favourite.json"
)


def save_favourites(favs):
    """
    Save a list of favourite movie IDs to the favourites file.

    Args:
        favs (list): List of movie IDs to add to favourites.

    Returns:
        None
    """
    try:
        # Load existing favourites if file exists
        if os.path.exists(FAVOURITE_PATH):
            with open(FAVOURITE_PATH, encoding="utf-8") as f:
                try:
                    existing_favs = json.load(f)
                except Exception:
                    existing_favs = []
        else:
            existing_favs = []

        # Attach new favourites (avoid duplicates)
        for fav in favs:
            if fav not in existing_favs:
                existing_favs.append(fav)

        with open(FAVOURITE_PATH, "w", encoding="utf-8") as f:
            json.dump(existing_favs, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved favourites: {existing_favs}")
    except Exception as e:
        logger.error(f"Error saving favourites: {e}")


def search_movie_id(movie_name):
    """
    Search for a movie by name and return its TMDb ID.

    Args:
        movie_name (str): Name of the movie to search for.

    Returns:
        str | None: TMDb movie ID if found, else None.
    """
    try:
        tmdb_api_key = os.getenv("TMDB_API_KEY", "")
        client = TMDbClient(api_key=tmdb_api_key)
        response = client.search_movie(movie_name)
        if response and len(response) > 0:
            movie_id = response[0]["id"]
            logger.info(f"Searched for movie '{movie_name}', returning id '{movie_id}'")
            return movie_id
        else:
            logger.error(f"No results found for movie '{movie_name}'")
            return None
    except Exception as e:
        logger.error(f"Error searching for movie '{movie_name}': {e}")
        return None


class AddFavouriteTool(BaseTool):
    """
    Tool to add a movie to favourites by its name.
    Input: movie name.
    Output: success message.
    """

    name: str = "add_favourite"
    description: str = "Add a movie to favourites. Input: movie name. Output: success message."

    def _run(self, movie_name: str):
        """
        Add a movie to favourites by searching for its name.

        Args:
            movie_name (str): Name of the movie to add.

        Returns:
            str: Success or error message.
        """
        movie_id = search_movie_id(movie_name)
        if not movie_id:
            return f"Movie '{movie_name}' not found. Cannot add to favourites."
        save_favourites([movie_id])
        logger.info(f"Added {movie_id} to favourites.")
        return f"Added {movie_id} to favourites."

    def _arun(self, movie_name: str):
        return self._run(movie_name)


class DeleteFavouriteTool(BaseTool):
    """
    Tool to delete a movie from favourites by its name.
    Input: movie name.
    Output: success message.
    """

    name: str = "delete_favourite"
    description: str = "Delete a movie from favourites. Input: movie name. Output: success message."

    def _run(self, movie_name: str):
        """
        Delete a movie from favourites by searching for its name.

        Args:
            movie_name (str): Name of the movie to delete.

        Returns:
            str: Success or error message.
        """
        try:
            movie_id = search_movie_id(movie_name)
            if not movie_id:
                return f"Movie '{movie_name}' not found. Cannot delete from favourites."
            if os.path.exists(FAVOURITE_PATH):
                with open(FAVOURITE_PATH, encoding="utf-8") as f:
                    fav_ids = json.load(f)
            else:
                fav_ids = []

            if movie_id in fav_ids:
                fav_ids.remove(movie_id)
                with open(FAVOURITE_PATH, "w", encoding="utf-8") as f:
                    json.dump(fav_ids, f, ensure_ascii=False, indent=2)
                logger.info(f"Deleted {movie_id} from favourites.")
                return f"Deleted {movie_id} from favourites."
            else:
                logger.info(f"Movie ID {movie_id} not found in favourites.")
                return f"Movie ID {movie_id} not found in favourites."
        except Exception as e:
            logger.error(f"Error deleting favourite {movie_id}: {e}")
            return f"Error deleting favourite {movie_id}: {e}"

    def _arun(self, movie_name: str):
        return self._run(movie_name)


class GetMovieDetailsTool(BaseTool):
    """
    Tool to get movie details by its TMDb ID.
    Input: movie name.
    Output: movie details as a string.
    """

    name: str = "get_movie_details"
    description: str = "Get movie details by its name. Input: movie name. Output: movie details as a string."

    def _run(self, movie_name: str):
        """
        Get details for a movie by searching for its name and TMDb ID.

        Args:
            movie_name (str): Name of the movie to get details for.

        Returns:
            str: Movie details or error message.
        """
        try:
            tmdb_api_key = os.getenv("TMDB_API_KEY", "")
            client = TMDbClient(api_key=tmdb_api_key)
            movie_id = search_movie_id(movie_name)
            if not movie_id:
                return f"Movie '{movie_name}' not found. Cannot get details."
            response = client.get_movie_details(movie_id)
            if response:
                logger.info(f"Retrieved details for movie ID {movie_id}")
                return response
        except Exception as e:
            logger.error(f"Error getting details for movie ID {movie_id}: {e}")
        return f"Error getting details for movie ID {movie_id}"

    def _arun(self, movie_id: str):
        return self._run(movie_id)
