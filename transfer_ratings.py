#!/usr/bin/env python
import datetime
import os
import sys
import time

from RatS.inserters.imdb_inserter import IMDBInserter
from RatS.inserters.movielense_inserter import MovielenseInserter
from RatS.parsers.imdb_parser import IMDBRatingsParser
from RatS.parsers.trakt_parser import TraktRatingsParser
from RatS.utils import file_impex

TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
EXPORTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'RatS', 'exports'))

PARSERS = ['TRAKT', 'IMDB']
INSERTERS = ['IMDB', 'MOVIELENSE']
PARSERS_DICT = {'TRAKT': TraktRatingsParser, 'IMDB': IMDBRatingsParser}
INSERTERS_DICT = {'IMDB': IMDBInserter, 'MOVIELENSE': MovielenseInserter}


def main(argv):
    if len(argv) != 3:
        print_help(argv)
        return
    if argv[1].upper() not in PARSERS_DICT:
        print('Parser %s not available' % argv[1])
        return
    if argv[2].upper() not in INSERTERS_DICT:
        print('Inserter %s not available' % argv[2])
        return

    execute(argv)


def print_help(argv):
    sys.stdout.write('''\r\nThe number of arguments was not correct!
        \r\nExample call:
        \r\n   python %s imdb movielense
        \r\nThis would parse your ratings from IMDB and insert them to your Movielense account
        \r\n''' % argv[0])
    sys.stdout.flush()


def get_parser_from_arg(param):
    try:
        return PARSERS_DICT[param.upper()]
    except KeyError:
        return None


def get_inserter_from_arg(param):
    try:
        return INSERTERS_DICT[param.upper()]
    except KeyError:
        return None


def execute(argv):
    # PARSING DATA
    parser = get_parser_from_arg(argv[1])()
    movies = parse_data_from_source(parser)
    # FILE LOADING
    # movies = load_data_from_file(filename)
    # POSTING THE DATA
    inserter = get_inserter_from_arg(argv[2])()
    insert_movie_ratings(inserter, movies)


def parse_data_from_source(parser):
    movies = parser.parse()
    json_filename = '%s_%s.json' % (TIMESTAMP, type(parser.site).__name__)
    file_impex.save_movies_json(movies, folder=EXPORTS_FOLDER, filename=json_filename)
    sys.stdout.write('\r\n===== %s: saved %i parsed movies to %s/%s\r\n' %
                     (type(parser.site).__name__, len(movies), EXPORTS_FOLDER, json_filename))
    sys.stdout.flush()
    return movies


def load_data_from_file(filename):
    movies = file_impex.load_movies_json(folder=EXPORTS_FOLDER, filename=filename)
    sys.stdout.write('\r\n===== loaded %i movies from %s/%s\r\n' % (len(movies), EXPORTS_FOLDER, filename))
    sys.stdout.flush()
    return movies


def insert_movie_ratings(inserter, movies):
    inserter.insert(movies)


if __name__ == "__main__":
    main(sys.argv)
