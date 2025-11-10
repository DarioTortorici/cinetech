from typing import Any

from cinetech.infrastructure.monitoring.logger import Logger

logger = Logger.get_logger("cinetech.conversation_context")


class ConversationContext:
    """
    Simple manager for conversation history and relevant entities (movies).

    Maintains a list of messages (role: 'user'|'assistant'|'system', content: str)
    and a dictionary of entities movie_id -> metadata.

    Provides methods to add messages, add relevant movies, and build a context block
    (e.g., the last N interactions plus a summary of relevant entities).
    """

    def get_favorite_movies(self) -> str:
        """
        Returns a string with the user's favorite movies, if available.
        Searches for movies stored with a 'favorite' True key or a 'favorite_movies' list in metadata.

        Returns:
            str: Comma-separated favorite movie titles or a message if none are stored.
        """
        # Search for movies with 'favorite' flag set to True
        favorites = [meta for meta in self.movies.values() if meta.get("favorite") is True]
        # If none found, look for a 'favorite_movies' list in metadata
        if not favorites:
            fav_list = []
            for meta in self.movies.values():
                fav_list.extend(meta.get("favorite_movies", []))
            if fav_list:
                return ", ".join(fav_list)
            return "No favorite movies stored."
        # Return titles of favorites
        return ", ".join([m.get("title", "") for m in favorites if m.get("title")]) or "No favorite movies stored."

    def __init__(self, max_history: int = 10):
        """
        Initialize the ConversationContext.

        Args:
            max_history (int): Maximum number of messages to keep in history.
        """
        self.max_history = max_history
        self.messages: list[dict[str, str]] = []
        self.movies: dict[str, dict[str, Any]] = {}
        self.chromadb_results: list[dict[str, str]] = []  # Each: {"query": str, "result": str}

    def _add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.

        Args:
            role (str): The role of the message sender ('user', 'assistant', 'system').
            content (str): The message content.

        Raises:
            ValueError: If role is not one of the allowed values.
        """
        if role not in {"user", "assistant", "system"}:
            raise ValueError("Role must be 'user', 'assistant' or 'system'")
        self.messages.append({"role": role, "content": content})
        # Trim history to max_history
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]
        logger.info(f"Added {role} message to conversation context.")

    def add_user_message(self, content: str) -> None:
        """
        Add a user message to the conversation history.

        Args:
            content (str): The user's message content.
        """
        self._add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """
        Add an assistant message to the conversation history.

        Args:
            content (str): The assistant's message content.
        """
        self._add_message("assistant", content)

    def add_system_message(self, content: str) -> None:
        """
        Add a system message to the conversation history.

        Args:
            content (str): The system message content.
        """
        self._add_message("system", content)

    def get_recent(self, n: int | None = None) -> list[dict[str, str]]:
        """
        Get the most recent n messages from the conversation history.

        Args:
            n (int | None): Number of messages to retrieve. If None, returns all.

        Returns:
            list: List of recent message dictionaries.
        """
        if n is None or n >= len(self.messages):
            return list(self.messages)
        return list(self.messages[-n:])

    def build_context_history(self, max_messages: int | None = None) -> str:
        """
        Returns a formatted string with the last `max_messages` messages.

        Used to insert conversation history into prompts.

        Args:
            max_messages (int | None): Number of messages to include. If None, includes all.

        Returns:
            str: Formatted conversation history.
        """
        msgs = self.get_recent(max_messages)
        lines = []
        for m in msgs:
            prefix = m["role"].capitalize()
            lines.append(f"{prefix}: {m['content']}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the conversation context to a dictionary.

        Returns:
            dict: Dictionary representation of the context.
        """
        return {
            "messages": list(self.messages),
            "movies": dict(self.movies),
            "chromadb_results": list(self.chromadb_results),
        }

    def clear(self) -> None:
        """
        Clear all conversation history, movies, and ChromaDB results.
        """
        self.messages.clear()
        self.movies.clear()
        self.chromadb_results.clear()
