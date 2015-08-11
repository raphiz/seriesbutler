from pyseries import functions
import os
from pyseries.providers import Solarmovie
from pyseries.datasources import TheTvDb


def test_download_fn_works_for_valid_url():
    try:
        url = "https://www.youtube.com/watch?v=Th4saUa7Ecw"
        assert functions.download(url, 'tests', 'example') is True
        assert os.path.exists('tests/example.m4a') is True
    finally:
        if os.path.exists('tests/example.m4a'):
            os.unlink('tests/example.m4a')


def test_download_fn_returns_false_for_valid_url():
    url = "https://example.com/stuff"
    assert functions.download(url, 'tests', 'example') is False


def test_has_suitable_extractor():
    youtube = "https://www.youtube.com/watch?v=Th4saUa7Ecw"
    nonsense = "https://example.com/stuff"
    vodlocker = "http://vodlocker.com/v4y2drplpx6v"

    assert functions._has_suitable_extractor(youtube) is True
    assert functions._has_suitable_extractor(vodlocker) is True
    assert functions._has_suitable_extractor(nonsense) is False


def test_load_series_returns_correct_list_of_series():
    link_providers = [Solarmovie()]
    datasource = TheTvDb()
    series = functions.load_series(
        'tests/examples/',
        link_providers,
        datasource
    )
    assert 2 == len(series)

    assert "House of Cards (US)" == series[0].name
    assert "tt1856010" == series[0].imdb_id
    # TODO: assert cfg
    assert "Breaking Bad" == series[1].name
    assert "tt0903747" == series[1].imdb_id
    # TODO: assert cfg
