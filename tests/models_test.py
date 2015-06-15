from pyseries.models import Configuration, Series, Episode
from nose.tools import *
from pyseries.providers import Solarmovie
from pyseries.datasources import TheTvDb

default_cfg = Configuration()
default_cfg.link_providers = [Solarmovie()]
default_cfg.datasource = TheTvDb()
default_cfg.ignored_hosters = ['played.to']
default_cfg.prefered_hosters = ['vodlocker.com']


def test_series_returns_episodes():
    series = Series("Breaking Bad", "tt0903747", default_cfg)
    episodes = series.episodes()
    assert_equals(62, len(episodes))
    assert_equals(series, episodes[4].series)
    assert_equals(1, episodes[4].season_no)
    assert_equals(5, episodes[4].episode_no)


def test_episodes_returns_links():
    series = Series("Breaking Bad", "tt0903747", default_cfg)

    episode = Episode(series, 1, 3)
    links = episode.links()
    assert_true(len(links) > 50)
    assert_equals('vodlocker.com', links[1].hoster)


def test_sort_episodes():
    s1e3 = Episode(None, 1, 3)
    s1e3_2 = Episode(None, 1, 3)

    s1e2 = Episode(None, 1, 2)
    s2e4 = Episode(None, 2, 4)

    episodes = sorted([s1e3, s1e3_2, s1e2, s2e4])
    assert_equals(s1e2, episodes[0])
    assert_equals(s1e3_2, episodes[1])
    assert_equals(s1e3, episodes[2])
    assert_equals(s2e4, episodes[3])
