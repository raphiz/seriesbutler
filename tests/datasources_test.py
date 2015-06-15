from pyseries.datasources import TheTvDb
from nose.tools import *


def test_tvdb_find_by_imdb_id():
    datasource = TheTvDb()
    assert_equals('Breaking Bad', datasource.name_for_imdb_id('tt0903747'))


def test_episodes_for_imdb_id():
    datasource = TheTvDb()
    episodes = datasource.episodes_for_imdb_id('tt0903747')
    assert_equals(62, len(episodes))
    assert_equals((2, 7), episodes[13])
