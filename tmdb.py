import requests
from flask import current_app
import urllib
import urllib.parse

"""
this file is a collation of interface functions for the TMDB API
"""


def search_movies(name):
    response = requests.get(url=build_url("search/movie", query=name))

    if response.status_code == 200:
        return response.json()

    # TODO: implement a custom error and raise it whenever status code is not 200


def get_movie_data(movie_id):
    response = requests.get(url=build_url("movie/" + str(movie_id)))
    return response.json()


def build_url(endpoint, **parameters):
    parameters["api_key"] = current_app.config['TMDB_API_KEY']

    url = urllib.parse.urljoin(current_app.config['TMDB_BASE_URL'], endpoint)
    url += "?" + urllib.parse.urlencode(parameters)

    return url
