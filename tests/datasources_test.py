from pyseries.datasources import TheTvDb


def test_tvdb_find_by_imdb_id():
    datasource = TheTvDb()
    assert 'Breaking Bad' == datasource.name_for_imdb_id('tt0903747')


def test_episodes_for_imdb_id():
    datasource = TheTvDb()
    episodes = datasource.episodes_for_imdb_id('tt0903747')
    assert 62 == len(episodes)
    assert (2, 7) == episodes[13]
