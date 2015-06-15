from pyseries.providers import Solarmovie, WatchTvSeries
from pyseries.datasources import TheTvDb
from nose.tools import *
from pyseries.models import Series, Episode, Configuration

default_cfg = Configuration()
default_cfg.link_providers = []
default_cfg.datasource = TheTvDb
default_cfg.ignored_hosters = ['played']
default_cfg.prefered_hosters = ['vodlocker']


def test_links_for_episode():
    series = Series("Breaking Bad", "tt0903747", default_cfg)
    episode = Episode(series, 2, 7)
    solarmovie = Solarmovie()
    links = solarmovie.links_for(episode)
    assert_true(len(links) > 25)
    one = episode.sort(links)[0].direct()
    assert_true(one.startswith('http://vodlocker.com/'))


def test_links_for_episode_WatchTvSeries():

    series = Series("Breaking Bad", "tt0903747", default_cfg)
    episode = Episode(series, 2, 7)
    watchTvSeries = WatchTvSeries()
    links = watchTvSeries.links_for(episode)
    assert_true(len(links) > 25)
    one = episode.sort(links)[0].direct()
    assert_true(one.startswith('http://vodlocker.com/'))
