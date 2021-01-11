import datetime
import hashlib
import os

from sqlalchemy.ext.hybrid import hybrid_property

from app import db


class Source(db.Model):
    __tablename__ = "sources"

    id = db.Column(db.Integer, primary_key=True)

    address = db.Column(db.String(256))

    def __init__(self, address):
        self.address = address

    def __repr__(self):
        return f"<Source {self.id}>"


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)

    filename = db.Column(db.String(256))
    path = db.Column(db.String(2048))

    # marked means that the data has been inferred from the filename
    _marked_codec = db.Column(db.String(16))
    _marked_edition = db.Column(db.String(32))
    _marked_resolution = db.Column(db.String(8))
    _marked_sample = db.Column(db.Boolean)
    _marked_source = db.Column(db.String(8))
    _marked_title = db.Column(db.String(256))
    _marked_year = db.Column(db.String(4))

    def set_marked_attr(self, attribute, value):
        setattr(self, attribute, value)
        self.generate_hash()

    # marked attributes setting is intercepted to update object hash
    marked_codec = hybrid_property(fget=lambda self: self._marked_codec,
                                   fset=lambda self, val: self.set_marked_attr("_marked_codec", val))
    marked_edition = hybrid_property(fget=lambda self: self._marked_edition,
                                     fset=lambda self, val: self.set_marked_attr("_marked_edition", val))
    marked_resolution = hybrid_property(fget=lambda self: self._marked_resolution,
                                        fset=lambda self, val: self.set_marked_attr("_marked_resolution", val))
    marked_sample = hybrid_property(fget=lambda self: self._marked_sample,
                                    fset=lambda self, val: self.set_marked_attr("_marked_sample", val))
    marked_source = hybrid_property(fget=lambda self: self._marked_source,
                                    fset=lambda self, val: self.set_marked_attr("_marked_source", val))
    marked_title = hybrid_property(fget=lambda self: self._marked_title,
                                   fset=lambda self, val: self.set_marked_attr("_marked_title", val))
    marked_year = hybrid_property(fget=lambda self: self._marked_year,
                                  fset=lambda self, val: self.set_marked_attr("_marked_year", val))

    obj_hash = db.Column(db.Integer)

    # tmdb data
    tmdb_id = db.Column(db.Integer)
    tmdb_last_checked = db.Column(db.DateTime)
    imdb_id = db.Column(db.String(10))
    title = db.Column(db.String(128))
    original_title = db.Column(db.String(128))
    overview = db.Column(db.String(1024))
    adult = db.Column(db.Boolean)
    popularity = db.Column(db.Float)
    release_date = db.Column(db.DateTime)
    revenue = db.Column(db.Integer)
    runtime = db.Column(db.Integer)
    status = db.Column(db.String(16))
    tagline = db.Column(db.String(512))
    vote_average = db.Column(db.Integer)
    vote_count = db.Column(db.Integer)

    files = db.relationship("File", secondary="movie_files")

    def __init__(self, path, filename, marked_codec=None, marked_edition=None, marked_resolution=None,
                 marked_sample=None, marked_source=None, marked_title=None, marked_year=None):
        self.created_at = datetime.datetime.utcnow()

        self.path = path
        self.filename = filename

        self.marked_codec = marked_codec
        self.marked_edition = marked_edition
        self.marked_resolution = marked_resolution
        self.marked_sample = marked_sample
        self.marked_source = marked_source
        self.marked_title = marked_title
        self.marked_year = marked_year

        self.generate_hash()

    def __repr__(self):
        return f"<Movie {self.id}>"

    @hybrid_property
    def file_type(self):
        return self.filename[self.filename.rfind("."):]

    def generate_hash(self):
        self.obj_hash = compute_hash(
            self.path, self.filename, self.marked_codec, self.marked_edition, self.marked_resolution,
            self.marked_sample, self.marked_source, self.marked_title, self.marked_year
        )

    def update_tmdb_general(self, response):
        self.tmdb_last_checked = datetime.datetime.now()
        self.tmdb_id = response["id"]
        self.imdb_id = response["imdb_id"]
        self.title = response["title"]
        self.original_title = response["original_title"]
        self.overview = response["overview"]
        self.adult = True if response["adult"] == "True" else False
        self.popularity = response["popularity"]
        self.release_date = datetime.datetime.strptime(response["release_date"], "%Y-%m-%d")
        self.revenue = response["revenue"]
        self.runtime = response["runtime"]
        self.status = response["status"]
        self.tagline = response["tagline"]
        self.vote_average = response["vote_average"]
        self.vote_count = response["vote_count"]

    @hybrid_property
    def tmdb_matched(self):
        return True if self.tmdb_id is not None else False

    @tmdb_matched.expression
    def tmdb_matched(cls):
        return cls.tmdb_id != None

    @property
    def parent_dir(self):
        """
        movies directories are split up based on a hash of the tmdb id (this is to ease the reaction of filesystems for
         large number of files)
        """
        return os.path.join("static", "media", "movies",
                            hashlib.md5(str(self.tmdb_id).encode('utf-8')).hexdigest().lower()[0])

    @property
    def dir(self):
        """movies are stored in directories based on tmdb id"""
        return os.path.join(self.parent_dir, str(self.tmdb_id))

    @property
    def web_parent_path(self):
        """
        movies directories are split up based on a hash of the tmdb id (this is to ease the reaction of filesystems for
         large number of files)
        """
        return os.path.join("media", "movies", hashlib.md5(str(self.tmdb_id).encode('utf-8')).hexdigest().lower()[0])

    @property
    def web_path(self):
        """movies are stored in directories based on tmdb id"""
        return os.path.join(self.web_parent_path, str(self.tmdb_id))

    def build_dir(self):
        if not os.path.isdir(self.parent_dir):
            os.mkdir(self.parent_dir)
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)


def compute_hash(*args):
    string = ""

    for arg in args:
        string += str(arg) if arg else "None"

    return hashlib.md5(string.encode('utf-8')).hexdigest()


class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)

    name = db.Column(db.String(64))
    type = db.Column(db.String(8))

    def __init__(self, name, type_="image"):
        self.name = name
        self.created_at = datetime.datetime.utcnow()
        self.type = type_

    def __repr__(self):
        return f"<File {self.name}>"


class MovieFile(db.Model):
    __tablename__ = "movie_files"

    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("files.id"), primary_key=True)
