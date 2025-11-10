from langchain.agents import create_agent
from langchain_groq import ChatGroq

from cinetech.domain.memory.conversation_context import ConversationContext
from cinetech.infrastructure.monitoring.logger import Logger

from .prompts.prompt_templates import system_prompt
from .tools.tmdb_tools import AddFavouriteTool, DeleteFavouriteTool, GetMovieDetailsTool

logger = Logger.get_logger("cinetech.agent")

# In-memory dictionary for per-user conversation contexts
_contexts: dict[str, ConversationContext] = {}


def get_context(user_id: str) -> ConversationContext:
    """
    Retrieve or create a ConversationContext for a given user.

    Args:
        user_id (str): Unique identifier for the user.

    Returns:
        ConversationContext: The user's conversation context.
    """
    if user_id not in _contexts:
        _contexts[user_id] = ConversationContext()
    return _contexts[user_id]


def start_model(model="llama-3.3-70b-versatile"):
    """
    Initialize and return the agent with tools and system prompt.

    Args:
        model (str): The model name to use for the agent. Defaults to "llama-3.3-70b-versatile".

    Returns:
        Agent: The initialized agent with tools and system prompt.

    Raises:
        Exception: For unexpected errors during initialization.
    """
    try:
        logger.info(f"Initializing agent with model: {model}")
        agent = ChatGroq(
            model=model,
            temperature=0.3,
            max_retries=2,
        )
        # Attach tools and system prompt to the agent
        agent = create_agent(
            agent,
            tools=[AddFavouriteTool(), DeleteFavouriteTool(), GetMovieDetailsTool()],
            system_prompt=system_prompt.format(),
        )
        logger.info("Agent created.")
        return agent
    except Exception as e:
        logger.exception(f"Error initializing agent: {e}")
        raise Exception(f"Error initializing agent: {e}") from e
