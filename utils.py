import datetime
import os
import string
from functools import reduce

sources = {"CAM": ["CAMRip", "CAM", "HDCAM"],
           "TeleSync": ["TS", "HDTS", "HD-TS", "TELESYNC", "PDVD", "PreDVDRip"],
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
                      "BD5", "BD9"],
           "HDRip": ["HDRip", "HD-Rip"]}
sources = {tag: key for key, tags in sources.items() for tag in tags}
current_year = datetime.datetime.now().year


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


def parse_source(name):
    """
    identifies source used in name
    returns the source and the tag used
    """

    letters = list(string.ascii_lowercase)

    name = name.lower()
    for tag in sources:
        tag_ = tag.lower()
        if tag_ in name or tag_.replace("-", " ") in name:
            if name[name.find(tag_) - 1] not in letters:
                return sources[tag], tag

    return "", ""


def parse_name(name):
    """
    simple name parsing to remove brackets, dots and spaces
    """

    name = name[:name.rfind('.')] if "." in name else name

    for replacer in ['(', ')', '.', '[', ']', '_']:
        name = name.replace(replacer, ' ')
        name = name.replace('  ', ' ')

    return name.strip(' ')


def parse_year(name):
    """
    iterates through the name with a 4-length window looking for appropriate years
    """

    length, i, year = len(name), int(4), int()
    while i < length + 1:
        try:
            int(name[i - 4:i])
            if name[i].lower() != 'p' and name[i - 1] != ' ' and name[i - 4] != ' ' and i != 4:
                year = name[i - 4:i]
                if 1900 <= int(year) <= current_year:
                    break
                else:
                    year = ""
        except ValueError:
            pass  # not integer
        except IndexError:  # last iteration
            try:
                year = name[i - 4:i] if len(str(abs(int(name[i - 4:i])))) == 4 else ""
                if 1900 <= int(year) <= current_year:
                    break
                else:
                    year = ""
            except ValueError:
                year = ""
        i += 1

    return year if year != 0 else ""


def parse_resolution(name):
    """
    iterates through the name with a 4-length window looking for a resolution
    """

    length, i, resolution = len(name), int(4), int()
    while i < length + 1:  # finds advertised resolution of movie (if present)
        try:
            int(name[i - 4:i])
            if name[i].lower() == 'p':
                resolution = name[i - 4:i + 1].strip(' ')
                return resolution if resolution != 0 else ""
        except ValueError:
            pass  # not an integer
        except IndexError:  # no resolution (or at least not recorded with traditional 'p' (e.g. 1080p)
            pass
        i += 1

    return ""


def parse_name_pt2(name, year=None, resolution=None, source=None):
    """reduces movie name up to year or resolution depending on which, if any, are present"""

    if year:
        name = name[:name.rfind(year)]

    elif resolution:
        name = name[:name.rfind(resolution)]

    elif source:
        name = name[:name.rfind(source)]

    return name.strip(' ').lower().title()


def process_files(files, folder_name=None):
    """
    parses files and extracts as much information as possible
    """

    for item, value in files.items():
        if value:  # if directory
            files[item] = process_files(value, folder_name=item)
        else:
            if item[-3:] in ['avi', 'mp4', 'mkv'] and "extra" not in folder_name.lower():
                files[item] = {
                    "file_type": item[-3:],
                    "source": "",
                    "sample": False
                }

                files[item]["source"], files[item]["source_tag"] = parse_source(item)
                files[item]["dir_source"], files[item]["dir_source_tag"] = parse_source(folder_name)

                name = parse_name(item)
                folder_name = parse_name(folder_name)

                files[item]["year"] = parse_year(name)
                files[item]["dir_year"] = parse_year(folder_name)

                files[item]["resolution"] = parse_resolution(name)
                files[item]["dir_resolution"] = parse_resolution(folder_name)

                if "sample" in item.lower():
                    files[item]["sample"] = True

                files[item]["name"] = parse_name_pt2(name,
                                                     year=files[item]["year"],
                                                     resolution=files[item]["resolution"],
                                                     source=files[item]["source_tag"])
                files[item]["dir_name"] = parse_name_pt2(folder_name,
                                                         year=files[item]["dir_year"],
                                                         resolution=files[item]["dir_resolution"],
                                                         source=files[item]["dir_source_tag"])

    return files


def flatten_movie_results(files, movies=None, _first_layer=True, _path=""):
    """
    filters out all movies from full list of extracted data and flattens the results

    _first_layer - tracks whether it is in the outer layer or not, used to determine what to return
    _path - tracks the file path
    """

    for item, value in files.items():
        if isinstance(value, dict):
            path = os.path.join(_path, item)
            if path[-1] == ":":  # for some reason join doesn't recognise windows drives :\
                path += "\\"
        else:
            path = _path

        if value and "name" not in value:
            files[item], movies = flatten_movie_results(value, movies, _first_layer=False, _path=path)
        else:
            if not movies:
                movies = []
            if value:
                if not value["sample"]:
                    dir_values = take_from_dir(value)
                    movies.append({
                        "marked": {
                            "title": value["dir_name"] if dir_values else value["name"],
                            "year": value["dir_year"] if dir_values else value["year"],
                            "file_type": value["file_type"],
                            "resolution": value["dir_resolution"] if dir_values else value["resolution"],
                            "sample": value["sample"],
                            "source": value["dir_source"] if dir_values else value["source"],
                            "original_filename": item
                        },
                        "path": _path
                    })

    if _first_layer:
        return movies

    return files, movies


def take_from_dir(values):
    """checks whether the movie details should be extracted from the filename or folder name"""

    file_score, dir_score = 0, 0

    attributes = ["year", "resolution", "source"]

    for attribute in attributes:
        if values[attribute]:
            file_score += 1

    for attribute in attributes:
        if values["dir_" + attribute]:
            dir_score += 1

    return dir_score > file_score
