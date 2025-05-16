import pickle
import streamlit as st
import requests

# OMDb fetch function with rating, plot, and genre
def fetch_movie_data(title):
    api_key = "61f16ece"
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return {
            "title": data.get("Title"),
            "poster": data.get("Poster"),
            "plot": data.get("Plot"),
            "rating": data.get("imdbRating"),
            "genre": data.get("Genre")
        }
    except:
        return None

# Updated recommend function
def recommend(movie, genre_filter=None):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ratings = []
    recommended_movie_plots = []
    recommended_movie_trailers = []

    count = 0
    for i in distances[1:]:
        if count >= 5:
            break
        title = movies.iloc[i[0]].title
        movie_data = fetch_movie_data(title)
        if movie_data:
            # Safely parse genre
            if genre_filter:
                genre_str = movie_data.get("genre")
                movie_genres = genre_str.split(", ") if genre_str else []
                if not any(g in movie_genres for g in genre_filter):
                    continue

            recommended_movie_names.append(movie_data['title'])

            poster = movie_data.get('poster')
            if not poster or poster == "N/A":
                poster = "https://via.placeholder.com/500x750?text=No+Image"
            recommended_movie_posters.append(poster)

            recommended_movie_ratings.append(movie_data.get("rating", "N/A"))
            recommended_movie_plots.append(movie_data.get("plot", "No plot available"))

            # YouTube trailer search link
            trailer_link = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}+trailer"
            recommended_movie_trailers.append(trailer_link)

            count += 1

    return recommended_movie_names, recommended_movie_posters, recommended_movie_ratings, recommended_movie_plots, recommended_movie_trailers

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.header('🎬 Movie Recommender System')

# Load data
movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

# Genre filter options
genre_filter = st.sidebar.multiselect(
    "🎭 Filter by Genre",
    ["Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", "Thriller"]
)

movie_list = movies['title'].values
selected_movie = st.selectbox("🎞️ Select a movie", movie_list)

if st.button('Show Recommendation'):
    names, posters, ratings, plots, trailers = recommend(selected_movie, genre_filter)

    if names:
        cols = st.columns(5)
        for i in range(len(names)):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])
                st.caption(f"⭐ IMDb: {ratings[i]}")
                st.caption(plots[i])
                st.markdown(f"[🎥 Watch Trailer]({trailers[i]})", unsafe_allow_html=True)
    else:
        st.warning("No recommendations match your selected genres.")
