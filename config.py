import os


class Config:
    MOVIE_DIR = os.environ.get("MOVIE_DIR")

    TMDB_BASE_URL = "https://api.themoviedb.org/3/"
    TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
