from unittest.mock import MagicMock, patch

from cinetech.application.ingestion_service import ingestion_service


def test_build_text_representation():
    """
    Test the build_text_representation function.
    Verifies that the returned text contains expected movie fields in Italian format.
    """
    movie = {
        "title": "Test Movie",
        "genres": "Drama",
        "director": "Director 1",
        "cast": "Actor 1",
        "year": "2020",
        "overview": "Test Overview",
    }
    text = ingestion_service.build_text_representation(movie)
    assert "Title: Test Movie." in text
    assert "Genres: Drama." in text
    assert "Director: Director 1." in text
    assert "Main cast: Actor 1." in text


@patch("cinetech.application.ingestion_service.ingestion_service.chromadb.PersistentClient")
def test_ingest_movies(mock_chromadb_client):
    """
    Test the ingest_movies function with a mocked ChromaDB client.
    Ensures that movies are added to the collection as expected.
    """
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_chromadb_client.return_value = mock_client
    mock_client.get_or_create_collection.return_value = mock_collection
    movies = [
        {
            "id": "1",
            "title": "Test Movie",
            "genres": "Drama",
            "director": "Director 1",
            "year": "2020",
            "rating": 8.5,
            "cast": "Actor 1",
            "overview": "Test Overview",
        }
    ]
    ingestion_service.ingest_movies(movies)
    mock_collection.add.assert_called()


@patch("cinetech.application.ingestion_service.ingestion_service.chromadb.PersistentClient")
def test_search_movies(mock_chromadb_client):
    """
    Test the search_movies function with a mocked ChromaDB client.
    Ensures that the search returns the expected movie metadata and description.
    """
    # Mock the response structure expected from LlamaIndex's query engine
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_chromadb_client.return_value = mock_client
    mock_client.get_or_create_collection.return_value = mock_collection

    # Create a mock node object with the required attributes
    class MockNode:
        def __init__(self):
            self.node = MagicMock()
            self.node.metadata = {
                "title": "Test Movie",
                "overview": "Test Movie Overview",
                "genres": "Drama",
                "director": "Director 1",
                "year": "2020",
                "cast": "Actor 1",
                "rating": 8.5,
            }
            self.score = 0.95

    mock_response = MagicMock()
    mock_response.source_nodes = [MockNode()]

    # Patch VectorStoreIndex and its methods
    with patch("cinetech.application.ingestion_service.ingestion_service.VectorStoreIndex") as mock_index_class:
        mock_index_instance = MagicMock()
        mock_index_class.from_vector_store.return_value = mock_index_instance
        mock_query_engine = MagicMock()
        mock_query_engine.query.return_value = mock_response
        mock_index_instance.as_query_engine.return_value = mock_query_engine

        results = ingestion_service.search_movies("query", top_k=1)
        assert len(results) == 1
        assert results[0]["title"] == "Test Movie"
        assert results[0]["overview"] == "Test Movie Overview"
        assert results[0]["genres"] == "Drama"
        assert results[0]["director"] == "Director 1"
        assert results[0]["year"] == "2020"
        assert results[0]["cast"] == "Actor 1"
        assert results[0]["score"] == 0.95
