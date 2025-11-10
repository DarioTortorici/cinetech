from unittest.mock import patch

import pytest

from cinetech.application.chat_service.chat_service import ChatService


class DummyContext:
    """
    Dummy context for testing ChatService methods.
    Simulates conversation history and movie lists.
    """

    def __init__(self):
        self.user_messages = []
        self.assistant_messages = []
        self.chromadb_results = []

    def build_context_history(self):
        """Return a dummy conversation history string."""
        return "history"

    def build_movies_list(self):
        """Return a dummy movies list string."""
        return "movies"

    def add_user_message(self, msg):
        """Add a user message to the context."""
        self.user_messages.append(msg)

    def add_assistant_message(self, msg):
        """Add an assistant message to the context."""
        self.assistant_messages.append(msg)

    def get_favorite_movies(self):
        """Return a dummy favorite movies string."""
        return "favorites"


def test_build_prompt():
    """
    Test that _build_prompt_vars returns correct prompt variables.
    """
    context = DummyContext()
    service = ChatService(context)
    prompt_vars = service._build_prompt_vars(user_message="Hello", reply="movies")
    assert isinstance(prompt_vars, dict)
    assert prompt_vars["conversation_history"] == "history"
    assert prompt_vars["favorite_movies"] == "favorites"
    assert prompt_vars["movies_list"] == "movies"
    assert prompt_vars["user_message"] == "Hello"


@patch("cinetech.application.chat_service.chat_service.ChatService._chat_with_agent")
def test_generate_reply_agent(mock_chat):
    """
    Test generate_reply with agent response.
    """
    mock_chat.return_value = "agent reply"
    context = DummyContext()
    service = ChatService(context)
    reply = service.generate_reply("Hello")
    assert reply == "agent reply"
    assert context.user_messages == ["Hello"]
    assert context.assistant_messages == ["agent reply"]


def test_generate_reply_empty():
    """
    Test that generate_reply raises ValueError on empty user message.
    """
    context = DummyContext()
    service = ChatService(context)
    with pytest.raises(ValueError):
        service.generate_reply("")


@patch("cinetech.application.chat_service.chat_service.start_model")
def test_chat_with_agent_error(mock_start_model):
    """
    Test that _chat_with_agent raises Exception on agent initialization failure.
    """
    mock_start_model.side_effect = Exception("fail")
    context = DummyContext()
    service = ChatService(context)
    with pytest.raises(Exception) as exc_info:
        service._chat_with_agent(
            {
                "conversation_history": "history",
                "favorite_movies": "favorites",
                "movies_list": "movies",
                "user_message": "Hello",
            }
        )
    assert "Error during agent interaction: fail" in str(exc_info.value)
