from dotenv import load_dotenv

from cinetech.application.ingestion_service.ingestion_service import search_movies
from cinetech.domain.agent import start_model
from cinetech.domain.memory.conversation_context import ConversationContext
from cinetech.domain.prompts.prompt_templates import chat_prompt
from cinetech.infrastructure.monitoring.logger import Logger

load_dotenv()

logger = Logger.get_logger("cinetech.chat_service")


class ChatService:
    """
    Constructs prompts from the conversation context and interacts with the llm model via `chat_with_agent`.

    Responsibilities:
    - Uses `ConversationContext` to retrieve conversation history and favorite movies
    - Builds prompt variables for the agent prompt
    """

    def __init__(self, context: ConversationContext):
        self.context = context
        logger.info("ChatService initialized.")

    def _build_prompt_vars(self, user_message: str, reply: str) -> dict:
        """
        Build the dictionary of variables for the Langchain prompt.

        Args:
            user_message (str): The user's message.
            reply (str): The replied movie list.

        Returns:
            dict: Variables for prompt construction.
        """
        return {
            "conversation_history": self.context.build_context_history(),
            "favorite_movies": self.context.get_favorite_movies(),
            "movies_list": reply,
            "user_message": user_message,
        }

    def generate_reply(self, user_message: str, chromadb_test: bool = False) -> str:
        """
        Generate a reply for the given `user_message` and update the conversation context.
        If chromadb_test=True, uses ChromaDB directly without the agent (for testing purposes).

        Args:
            user_message (str): The user's message to respond to.
            chromadb_test (bool): If True, bypasses agent and uses ChromaDB directly.

        Returns:
            str: The generated reply.

        Raises:
            ValueError: If user_message is empty or not a string.
        """
        if not isinstance(user_message, str) or not user_message.strip():
            logger.warning("Empty user message received.")
            raise ValueError("user_message must be a non-empty string")

        self.context.add_user_message(user_message)

        if chromadb_test:
            try:
                reply = search_movies(user_message, top_k=5)
            except Exception:
                reply = "Sorry, ChromaDB search is currently unavailable."
                logger.error("ChromaDB search failed.")
        else:
            try:
                llama_reply = search_movies(user_message, top_k=5)
                logger.info("ChromaDB enrichment successful.")
            except Exception:
                logger.error("ChromaDB enrichment failed.")
                reply = "Sorry, I am unable to generate a reply at the moment. Please try again later."
            try:
                prompt_vars = self._build_prompt_vars(user_message, llama_reply)
                reply = self._chat_with_agent(prompt_vars)
                logger.info("Agent response successfully generated.")
            except Exception:
                reply = "Sorry, I am unable to generate a reply at the moment. Please try again later."
                logger.error("Agent interaction failed.")
        self.context.add_assistant_message(reply)
        return reply

    def _chat_with_agent(self, prompt_vars: dict) -> str:
        """
        Interact with the agent using the provided prompt variables, formatted with chat_prompt.

        Args:
            prompt_vars (dict): Variables for the Langchain prompt.

        Returns:
            str: The response message from the agent, suitable for frontend display.

        Raises:
            ValueError: If prompt_vars is not a dict or missing required keys.
            Exception: For unexpected errors during agent interaction.
        """
        try:
            agent = start_model()
            # Format the prompt using chat_prompt
            formatted_prompt = chat_prompt.format(**prompt_vars)
            response = agent.invoke({"messages": [{"role": "user", "content": formatted_prompt}]})

            # Always extract the final message for frontend display
            last_msg = None
            if isinstance(response, dict) and "messages" in response:
                messages = response["messages"]
                if messages:
                    last_msg_obj = messages[-1]
                    # If it's a dict or an object with a 'content' attribute
                    if isinstance(last_msg_obj, dict):
                        last_msg = last_msg_obj.get("content", str(last_msg_obj))
                    else:
                        last_msg = getattr(last_msg_obj, "content", str(last_msg_obj))
                if last_msg is None:
                    last_msg = str(response)
                return last_msg.strip()
            # If response is a string, just return it
            if isinstance(response, str):
                return response.strip()
            return str(response)
        except ValueError as e:
            logger.error(f"Input error: {e}")
            raise ValueError(f"Input error: {e}") from e
        except Exception as e:
            logger.exception(f"Error during agent interaction: {e}")
            raise Exception(f"Error during agent interaction: {e}") from e
