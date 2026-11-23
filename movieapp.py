
import pickle
import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

st.set_page_config(page_title="MovieFlix", page_icon="🎬", layout="wide")

API_KEY = st.secrets["TMDB_API_KEY"]

session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

@st.cache_data(show_spinner=False)
def fetch_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        d = session.get(url, timeout=10).json()
        path = d.get("poster_path")
        return {
            "poster": "https://image.tmdb.org/t/p/w500" + path if path else None,
            "rating": round(d.get("vote_average", 0), 1),
            "year": (d.get("release_date") or "")[:4],
        }
    except requests.exceptions.RequestException:
        return {"poster": None, "rating": 0, "year": ""}

def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    results = []
    for i in neighbors[index][:5]:
        row = movies.iloc[i]
        info = fetch_details(row.movie_id)
        info["title"] = row.title
        results.append(info)
    return results

movies = pd.DataFrame(pickle.load(open("movie_dict.pkl", "rb")))
neighbors = pickle.load(open("neighbors.pkl", "rb"))

# ---------- MovieFlix banner ----------
st.markdown("""
<style>
.hero {
background: linear-gradient(120deg, #141414 35%, #b20710 100%);
padding: 35px 40px;
border-radius: 14px;
margin-bottom: 20px;
}
.hero h1 {
color: #ffffff;
font-size: 38px;
font-weight: 700;
margin: 0 0 14px 0;
padding: 0;
}
.hero h3 {
color: #ffffff;
font-size: 20px;
font-weight: 600;
margin: 0 0 6px 0;
padding: 0;
}
.hero p {
color: #cfcfcf;
font-size: 14px;
margin: 0;
}
</style>
<div class="hero">
<h1>🎬 MovieFlix</h1>
<h3>AI Powered Movie Recommendation System</h3>
<p>Get personalized movie recommendations instantly.</p>
</div>
""", unsafe_allow_html=True)
# --------------------------------------

selected_movie_name = st.selectbox("Select a movie", movies["title"].values)

if st.button("🎯 Recommend"):
    with st.spinner("Finding movies for you..."):
        results = recommend(selected_movie_name)

    st.subheader(f"Because you liked: {selected_movie_name}")
    cols = st.columns(5)
    for col, r in zip(cols, results):
        with col:
            with st.container(border=True):
                st.markdown(f"**{r['title']}**")
                if r["poster"]:
                    st.image(r["poster"])
                else:
                    st.caption("Poster not available")
                st.caption(f"⭐ {r['rating']}  •  {r['year']}")

st.divider()
st.caption("This product uses the TMDB API but is not endorsed or certified by TMDB.")