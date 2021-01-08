import datetime
import os
import re
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
sources = {tag: source for source, tags in sources.items() for tag in tags}  # reverses the above dictionary

editions = {
    "Limited": ["limited"],
    "Unrated": ["unrated", "unrated edition"],
    "Extended Cut": ["extended cut", " ec ", "extended cut edition", "extended"],
    "Anniversary Edition": ["anniversary edition", "anniversary special edition"],
    "Directors Cut": ["directors cut", "director's cut", "directors edition", "director's edition",
                      "directors definitive edition", "director's definitive edition", "extended directors cut",
                      "extended director's cut"],
}
editions = {tag: edition for edition, tags in editions.items() for tag in tags}  # reverses the above dictionary

codecs = {
    "H.264": ["h.264", "h264", "x.264", "x264"],
    "H.265": ["h.265", "h265", "x.265", "x265", "hevc"]
}
codecs = {tag: codec for codec, tags in codecs.items() for tag in tags}  # reverses the above dictionary

current_year = datetime.datetime.now().year
letters = list(string.ascii_lowercase)


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

    for tag in sources:
        name_lower = name.lower()
        try:
            tag_index = name_lower.index(tag.lower())
            if name_lower[tag_index - 1] not in letters:
                return sources[tag], name[tag_index:tag_index + len(tag)]
        except ValueError:
            pass

    return "", ""


def parse_edition(name):
    """
    identifies edition used in name
    returns the edition and the tag used
    """

    for edition_tag in editions:
        try:
            tag_index = name.lower().index(edition_tag)
            if name[tag_index - 1] not in letters:
                return editions[edition_tag], name[tag_index:tag_index + len(edition_tag)]
        except ValueError:
            pass

    return "", ""


def parse_codec(name):
    """
    identifies codec used in name
    returns the codec and the tag used
    """

    for codec_tag in codecs:
        name_lower = name.lower()
        try:
            tag_index = name_lower.index(codec_tag.lower())
            if name_lower[tag_index - 1] not in letters:
                return codecs[codec_tag], name[tag_index:tag_index + len(codec_tag)]
        except ValueError:
            pass

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
                return resolution.lower() if resolution != 0 else ""
        except ValueError:
            pass  # not an integer
        except IndexError:  # no resolution (or at least not recorded with traditional 'p' (e.g. 1080p)
            pass
        i += 1

    return ""


def parse_name_pt2(name, year=None, resolution=None, source=None, edition=None):
    """reduces movie name up to year or resolution depending on which, if any, are present"""

    attributes = {}
    for attribute in [year, resolution, source, edition]:
        if attribute:
            attributes[attribute] = name.find(attribute)

    if attributes:
        name = name[:name.rfind(min(attributes, key=attributes.get))]

    name = string.capwords(name.strip(' ').lower())  # TODO: hyphened words should have capitals on second part as well

    name = parse_roman_numerals(name)

    return name


def parse_roman_numerals(name):
    parsed_name = ""

    words = name.split()
    for index, word in enumerate(words):
        if bool(re.search(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", word.upper())):
            word = word.upper()
        parsed_name += word + " " if index < len(words) - 1 else word

    return parsed_name


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

                files[item]["edition"], files[item]["edition_tag"] = parse_edition(item)
                files[item]["dir_edition"], files[item]["dir_edition_tag"] = parse_edition(folder_name)

                files[item]["codec"], files[item]["codec_tag"] = parse_codec(item)
                files[item]["dir_codec"], files[item]["dir_codec_tag"] = parse_codec(folder_name)

                if "sample" in item.lower():
                    files[item]["sample"] = True

                files[item]["name"] = parse_name_pt2(name,
                                                     year=files[item]["year"],
                                                     resolution=files[item]["resolution"],
                                                     source=files[item]["source_tag"],
                                                     edition=files[item]["edition_tag"])
                files[item]["dir_name"] = parse_name_pt2(folder_name,
                                                         year=files[item]["dir_year"],
                                                         resolution=files[item]["dir_resolution"],
                                                         source=files[item]["dir_source_tag"],
                                                         edition=files[item]["dir_edition_tag"])

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
                            "edition": value["dir_edition"] if dir_values else value["edition"],
                            "codec": value["dir_codec"] if dir_values else value["codec"],
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

    attributes = ["year", "resolution", "source", "edition"]

    for attribute in attributes:
        if values[attribute]:
            file_score += 1

    for attribute in attributes:
        if values["dir_" + attribute]:
            dir_score += 1

    return dir_score > file_score


def get_flat_movies(*sources):
    """retrieves list of all movies in selected sources in a flat format"""

    files = {}
    for source in sources:
        key = source.address[:source.address.rfind("\\")]
        if key not in files:
            files[key] = {}

        files[source.address[:source.address.rfind("\\")]].update(get_directory_structure(source.address))

    process_files(files)

    movie_list = flatten_movie_results(files)
    return sorted(movie_list, key=lambda key: key["marked"]["year"].lower()) if movie_list else []
