import os

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface_api import HuggingFaceInferenceAPIEmbedding
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.vector_stores.chroma import ChromaVectorStore
from tqdm import tqdm

from cinetech.infrastructure.api.tmdb.themoviedb import TMDbClient
from cinetech.infrastructure.monitoring.logger import Logger

load_dotenv()

NUM_MOVIES = 100  # 3 min. required
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "../../infrastructure/db/chroma_db")

logger = Logger.get_logger("cinetech.ingestion_service")


def fetch_movies_from_tmdb(tmdb_api_key, num_movies=100):
    """
    Fetches popular movies from TMDB and returns a list of dictionaries using TMDbClient.

    Args:
        tmdb_api_key (str): TMDB API key for authentication.
        num_movies (int): Number of movies to fetch.

    Returns:
        list: List of movie dictionaries with details.
    """
    client = TMDbClient(api_key=tmdb_api_key)
    movies = []
    page = 1
    logger.info(f"Starting to fetch up to {num_movies} movies from TMDB.")
    while len(movies) < num_movies:
        try:
            top_rated = client.get_top_rated(page=page)
        except Exception as e:
            logger.error(f"Error fetching top rated movies from TMDB (page {page}): {e}")
            break
        for m in top_rated:
            movie_id = m["id"]
            try:
                details = client.get_movie_details(movie_id)
                credits = client.get_movie_credits(movie_id)
            except Exception as e:
                logger.error(f"Error fetching details/credits for movie ID {movie_id}: {e}")
                continue
            genres = [g["name"] for g in details.get("genres", [])]

            # Cast already limited to top 5 members in TMDbClient
            cast = [c["name"] for c in credits.get("cast", [])]
            directors = [d["name"] for d in credits.get("director", [])]

            movies.append(
                {
                    "id": str(movie_id),
                    "title": details.get("title"),
                    "overview": details.get("overview"),
                    "genres": ", ".join(genres),
                    "cast": ", ".join(cast),
                    "director": ", ".join(directors),
                    "year": details.get("release_date", "")[:4],
                    "rating": details.get("vote_average"),
                }
            )

            if len(movies) >= num_movies:
                logger.info(f"Reached requested number of movies: {num_movies}")
                break
        page += 1

    logger.info(f"Fetched {len(movies)} movies from TMDB.")
    return movies


def build_text_representation(movie):
    """
    Creates a rich textual string for embedding purposes.

    Args:
        movie (dict): Dictionary containing movie details.

    Returns:
        str: Textual representation of the movie for embedding.
    """
    return (
        f"Title: {movie['title']}. "
        f"Genres: {movie['genres']}. "
        f"Director: {movie['director']}. "
        f"Main cast: {movie['cast']}. "
        f"Year: {movie['year']}. "
        f"Overview: {movie['overview']}"
    )


embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")


def ingest_movies(movies):
    """
    Ingests movies into ChromaDB vector database.

    Args:
        movies (list): List of movie dictionaries to ingest.

    Returns:
        None
    """
    logger.info(f"Starting ingestion of {len(movies)} movies into ChromaDB.")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name="movies", embedding_function=embedding_fn)

    for m in tqdm(movies, desc="Ingesting movies"):
        text = build_text_representation(m)
        metadata = {
            "title": m["title"],
            "overview": m["overview"],
            "genres": m["genres"],
            "director": m["director"],
            "cast": m["cast"],
            "year": m["year"],
            "rating": m["rating"],
        }
        try:
            collection.add(ids=[m["id"]], documents=[text], metadatas=[metadata])
        except Exception as e:
            logger.error(f"Error ingesting movie '{m['title']}' (ID: {m['id']}): {e}")
    logger.info(f"Ingestion completed ({len(movies)} movies).")


def search_movies(query: str, top_k: int = 5):
    """
    Performs a semantic search on ChromaDB using LlamaIndex and returns the most relevant movies.

    Args:
        query (str): The search query.
        top_k (int): Number of results to return.

    Returns:
        list: List of movies sorted by relevance.
    """
    logger.info(f"Starting semantic search for query: '{query}' (top_k={top_k})")
    Settings.embed_model = HuggingFaceInferenceAPIEmbedding(
        model_name="sentence-transformers/all-mpnet-base-v2", token=HF_API_KEY
    )

    Settings.llm = HuggingFaceInferenceAPI(
        # model_name="deepseek-ai/DeepSeek-R1-0528",
        model_name="mistralai/Mistral-7B-Instruct-v0.2",
        token=HF_API_KEY,
        provider="auto",
    )
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    vector_store = ChromaVectorStore(chroma_collection=chroma_client.get_or_create_collection("movies"))
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=Settings.embed_model)

    try:
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        response = query_engine.query(query)
    except Exception as e:
        logger.error(f"Error during semantic search: {e}")
        return []
    ranked_movies = []
    for node in getattr(response, "source_nodes", []):
        ranked_movies.append(
            {
                "title": node.node.metadata.get("title", "Unknown"),
                "overview": node.node.metadata.get("overview", ""),
                "genres": node.node.metadata.get("genres", ""),
                "cast": node.node.metadata.get("cast", ""),
                "director": node.node.metadata.get("director", ""),
                "year": node.node.metadata.get("year", ""),
                "score": node.score,
            }
        )
    return ranked_movies


if __name__ == "__main__":
    logger.info("Loading data from TMDB...")
    movies_data = fetch_movies_from_tmdb(TMDB_API_KEY, NUM_MOVIES)

    logger.info("Ingesting into LlamaIndex/Chroma vector database...")
    ingest_movies(movies_data)

    logger.info("Test query: Psychological Thriller with Leonardo DiCaprio")
    movies = search_movies("Psychological Thriller with Leonardo DiCaprio", top_k=5)

    logger.info(f"Search results: {len(movies)} movies found.")
    for m in movies:
        logger.info(f"- {m['title']} ({m['year']}): {m['genres']} | Director: {m['director']}")
    logger.info(f"  {m['description']}\n  (score: {m['score']:.2f})\n")
