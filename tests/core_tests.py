from nose.tools import *
import pyseries
from configobj import ConfigObj


def test_fetch_url():
    result = pyseries.fetch_url('tt1856010')
    assert_equals('https://www.solarmovie.is/tv/house-of-cards-2013/', result)


def test_is_valid_config():
    valid = pyseries.is_valid_config('tests/examples/HouseOfCards/info.ini')
    assert_true(valid)

    #  TODO: test if it's for the right reason...
    invalid = pyseries.is_valid_config('tests/examples/nonsense/info.ini')
    assert_false(invalid)


def test_scrape_episodes():
    res = pyseries.scrape_episodes(
        'https://www.solarmovie.is/tv/breaking-bad-2008/'
    )
    assert_equals(5, len(res))
    assert_equals(7, len(res[1]['episodes']))
    assert_equals(13, len(res[2]['episodes']))
    assert_equals(13, len(res[3]['episodes']))
    assert_equals(13, len(res[4]['episodes']))
    assert_equals(16, len(res[5]['episodes']))
    assert_equals('September 18, 2011', res[4]['episodes'][10]['date'])


def test_remove_unwanted():
    path = 'tests/examples/BreakingBad'

    config = ConfigObj('tests/examples/BreakingBad/info.ini')

    everything = pyseries.scrape_episodes(
        'https://www.solarmovie.is/tv/breaking-bad-2008/'
    )

    reduced = pyseries.remove_unwanted(everything, config, path, True)
    assert_equals(3, len(reduced))
    assert_equals(4, len(reduced[3]['episodes']))

    everything = pyseries.scrape_episodes(
        'https://www.solarmovie.is/tv/breaking-bad-2008/'
    )

    reduced = pyseries.remove_unwanted(everything, config, path, False)
    assert_equals(2, len(reduced))
    assert_equals(4, len(reduced[4]['episodes']))


def test_unwrap():
    res = pyseries.unwrap(
        'http://solarmovie.is/link/play/4661337/'
    )
    assert_equals('http://streamin.to/eef35xoiizqp', res)
    res = pyseries.unwrap(
        'http://solarmovie.is/link/play/4800044/'
    )
    assert_equals('http://vodlocker.com/embed-2nqj4im2d3tp-640x360.html', res)

# These tests take a LOT of time...
# def test_download_link():
#     res = pyseries.download_link(
#         'https://www.solarmovie.is/tv/breaking-bad-2008/season-5/episode-16/',
#         'tests/examples/BreakingBad/',
#         's5e16'
#     )
#
# def test_download():
#     pyseries.download('tests/examples/')
