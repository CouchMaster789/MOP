import requests
from flask import current_app
import urllib
import urllib.parse

"""
this file is a collation of interface functions for the TMDB API
"""


def search_movies(name, year=None):
    response = requests.get(url=build_url("search/movie", query=name, year=year))

    if response.status_code == 200:
        return response.json()

    # TODO: implement a custom error and raise it whenever status code is not 200


def get_movie_data(movie_id):
    response = requests.get(url=build_url("movie/" + str(movie_id)))
    return response.json()


def get_movie_images_data(movie_id, language="en"):
    response = requests.get(url=build_url("movie/" + str(movie_id) + "/images", language=language))
    return response.json()


def get_image(file_path):
    response = requests.get(url=build_url(file_path, image=True))
    return response.content


def build_url(endpoint, image=False, **parameters):
    parameters["api_key"] = current_app.config['TMDB_API_KEY']

    parameters = {k: v for k, v in parameters.items() if v}

    if image:
        base_url = current_app.config['TMDB_IMAGE_URL'] + "original/"
    else:
        base_url = current_app.config['TMDB_BASE_URL']

    url = urllib.parse.urljoin(base_url, endpoint.strip("/"))
    if not image:
        url += "?" + urllib.parse.urlencode(parameters)

    return url
