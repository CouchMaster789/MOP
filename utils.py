import os
import string
from functools import reduce

sources = {"CAM": ["CAMRip", "CAM", "HDCAM"],
           "TeleSync": ["TS", "HDTS", "HD-TS", "TELESYNC", "PDVD", "PreDVDRip", "DTS-HD"],
           "WorkPrint": ["WP", "WORKPRINT", "WORK-PRINT"],
           "Telecine": ["TC", "HDTC", "HD-TC", "TELECINE"],
           "Screener": ["SCR", "SCREENER", "DVDSCR", "DVD-SCR", "DVDSCREENER", "DVD-SCREENER", "BDSCR"],
           "Digital Distribution Copy": ["DDC"],
           "R5": ["R5"],
           "DVD-R": ["DVDR", "DVD-R", "DVD-Full", "Full-Rip", "ISO"],
           "DVD Rip": ["DVDRip", "DVD-Rip", "DVDMux"],
           "HDTV": ["DSR", "DSRip", "SATRip", "DTHRip", "DVBRip", "HDTV", "HD-TV", "PDTV", "TVRip", "HDTVRip"],
           "VODRip": ["VODRip", "VODR"],
           "WEB-Rip": ["WEBRip", "WEB-Rip", "WEB"],
           "WEB-DL": ["WEBDL", "WEB-DL", "HDRip", "WEB-DLRip"],
           "WEBCap": ["WEB-Cap", "WEBCAP"],
           "BluRay": ["Blu-Ray", "BluRay", "BDRip", "BD-Rip", "BRRip", "BR-Rip", "BDMV", "BDR", "BD25", "BD50",
                      "BD5", "BD9"]}  # TODO: reverse the structure of this dictionary for a speed improvement


def get_directory_structure(root_directory):
    """
    Creates a nested dictionary that represents the folder structure of root_directory
    """

    directory = {}
    root_directory = root_directory.rstrip(os.sep)
    start = root_directory.rfind(os.sep) + 1

    for path, dirs, files in os.walk(root_directory):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], directory)
        parent[folders[-1]] = subdir

    return directory


def process_files(files):
    """
    parses files and extracts as much information as possible
    """

    for item, value in files.items():
        if value:  # if directory
            files[item] = process_files(value)
        else:
            if item[-3:] in ['avi', 'mp4', 'mkv']:
                files[item] = {
                    "file_type": item[-3:],
                    "source": "",
                    "sample": False
                }

                # parse source
                letters = list(string.ascii_lowercase)
                for source in sources.values():  # iterates through all of the sources looking for a match
                    for tag in source:
                        if tag.lower() in item.lower() or tag.lower().replace("-", " ") in item.lower():
                            if item[item.lower().index(tag.lower()) + 1].lower() not in letters \
                                    or item[item.lower().index(tag.lower()) - 1].lower() not in letters:
                                files[item]["source"] = list(sources.keys())[list(sources.values()).index(source)]

                # parse name
                name = item[:item.rfind('.')] if "." in item else item

                for replacer in ['(', ')', '.', '[', ']', '_']:
                    name = name.replace(replacer, ' ')
                    name = name.replace('  ', ' ')
                name = name.strip(' ')

                # parse year
                length, i, year = len(name), int(4), int()
                while i < length + 1:  # finds year of movie (if present)
                    try:
                        int(name[i - 4:i])
                        if name[i] != 'p' and name[i] != 'P' and name[i - 1] != ' ' and name[i - 4] != ' ' and i != 4:
                            year = name[i - 4:i]
                    except ValueError:
                        pass  # not integer
                    except IndexError:  # last iteration
                        year = name[i - 4:i] if len(name) > 4 else 0
                    i += 1
                files[item]["year"] = year

                # parse resolution
                length, i, resolution = len(name), int(4), int()
                while i < length + 1:  # finds advertised resolution of movie (if present)
                    try:
                        int(name[i - 4:i])
                        if name[i] == 'p' or name[i] == "P":
                            resolution = name[i - 4:i].strip(' ')
                    except ValueError:
                        pass  # not an integer
                    except IndexError:  # no resolution (or at least not recorded with traditional 'p' (e.g. 1080p)
                        pass
                    i += 1
                files[item]["resolution"] = resolution

                try:
                    name = name[:name.rfind(year)].strip(' ')
                except TypeError:  # no year present
                    try:
                        name = name[:name.rfind(resolution)].strip(' ')
                    except TypeError:  # no resolution present
                        pass

                if "sample" in item.lower():
                    files[item]["sample"] = True

                files[item]["name"] = name

    return files


def get_movie_names(files, movies=None, _first_layer=True):
    """
    filters out all movie names from full list of extracted data
    """

    for item, value in files.items():
        if value and "name" not in value:
            files[item], movies = get_movie_names(value, movies, _first_layer=False)
        else:
            if not movies:
                movies = []
            if value:
                if not value["sample"]:
                    movies.append(value["name"])

    if _first_layer:
        return movies

    return files, movies
