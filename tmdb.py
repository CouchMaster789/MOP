import requests
from flask import current_app
import urllib
import urllib.parse

"""
this file is a collation of interface functions for the TMDB API
"""


def get_movie_data(name):
    base_url = current_app.config['TMDB_BASE_URL']
    api_key = current_app.config['TMDB_API_KEY']

    response = requests.get(url=build_url(base_url, "search/movie", api_key=api_key, query=name))

    if response.status_code == 200:
        if response.json()["total_results"]:
            response = requests.get(
                url=build_url(base_url, "movie/" + str(response.json()["results"][0]["id"]), api_key=api_key))
            return response.json()


def build_url(base_url, endpoint, **parameters):
    url = urllib.parse.urljoin(base_url, endpoint)
    url += "?" + urllib.parse.urlencode(parameters)

    return url
