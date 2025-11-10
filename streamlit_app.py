import json
import os

import streamlit as st
from dotenv import load_dotenv

from cinetech.application.chat_service.chat_service import ChatService
from cinetech.domain.agent import get_context
from cinetech.infrastructure.api.tmdb.themoviedb import TMDbClient

load_dotenv()

# Configure Streamlit page
st.set_page_config(page_title="Cinetech Chat", layout="wide")
st.title("Cinetech Movie Recommendation Chat")

# Initialize session state variables for chat history, favorites, and user ID
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "favorites" not in st.session_state:
    st.session_state["favorites"] = set()
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "user1"  # For demo purposes, static user

# Layout: chat history (left column), favorites (right column)
col_chat, col_fav = st.columns([3, 1])

with col_chat:
    st.subheader("Chat History")
    # Render all chat messages inside a single scrollable container
    chat_html = "<div id='chat-container' style='max-height: 40vh; overflow-y: auto; padding-right: 8px;'>"
    for _i, (user, bot) in enumerate(st.session_state["chat_history"]):
        chat_html += (
            f"<div style='display: flex; justify-content: flex-end; margin-bottom: 2px;'>"
            f"<div style='background-color: #DCF8C6; color: #000; padding: 10px 16px;"
            f"border-radius: 18px 18px 0px 18px; max-width: 70%; "
            f"box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-size: 16px;'>{user}</div>"
            f"</div>"
        )
        chat_html += (
            f"<div style='display: flex; justify-content: flex-start; margin-bottom: 12px;'>"
            f"<div style='background-color: #F1F0F0; color: #000; padding: 10px 16px;"
            f"border-radius: 18px 18px 18px 0px; max-width: 70%; "
            f"box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-size: 16px;'>{bot}</div>"
            f"</div>"
        )
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # Chat input bar below chat history
    st.markdown("---")
    user_message = st.text_input("Send a message (in English) to Cinetech Agent:", "", key="chat_input")
    if st.button("Send") and user_message:
        # Generate agent reply and update chat history
        context = get_context(st.session_state["user_id"])
        chat_service = ChatService(context)
        try:
            reply = chat_service.generate_reply(user_message)
        except Exception as e:
            reply = f"Error: {e}"
        st.session_state["chat_history"].append((user_message, reply))
        st.rerun()

# Display user's favorite movies with posters
with col_fav:
    st.subheader("Your Favorite Films")

    tmdb_client = TMDbClient(api_key=os.getenv("TMDB_API_KEY", ""))
    fav_path = os.path.join("src", "cinetech", "infrastructure", "db", "favourite.json")
    try:
        with open(fav_path) as f:
            fav_ids = json.load(f)
    except Exception as e:
        fav_ids = []
        st.error(f"Could not read favorites: {e}")

    if fav_ids:
        for movie_id in fav_ids:
            try:
                # Get and display movie poster
                poster_suburl = tmdb_client.get_movie_poster(str(movie_id))
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_suburl}" if poster_suburl else None
                if poster_url:
                    st.markdown(
                        f"<img src='{poster_url}' alt='Movie poster' "
                        f"style='max-width:40%; display:block; margin:auto;'/>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Movie ID: {movie_id}")
                else:
                    st.write(f"No poster found for Movie ID: {movie_id}")
            except Exception as e:
                st.write(f"Error fetching poster for {movie_id}: {e}")
    else:
        st.write("No favorites yet. Tell the agent your favorite films and the pictures will appear here.")
