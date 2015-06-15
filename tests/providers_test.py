from pyseries.providers import Solarmovie
from pyseries.datasources import TheTvDb
from nose.tools import *
from pyseries.models import Series, Episode, Configuration

default_cfg = Configuration()
default_cfg.link_providers = []
default_cfg.datasource = TheTvDb
default_cfg.ignored_hosters = ['played.to']
default_cfg.prefered_hosters = ['vodlocker.com']


def test_links_for_episode():
    series = Series("Breaking Bad", "tt0903747", default_cfg)
    episode = Episode(series, 2, 7)
    solarmovie = Solarmovie()
    links = solarmovie.links_for(episode)

    assert_true(len(links) > 25)
    # This is actually a really shitty test that MUST be improved...
    assert_equals("http://", links[0].direct()[:7])
