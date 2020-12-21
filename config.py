import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    TMDB_BASE_URL = "https://api.themoviedb.org/3/"
    TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
