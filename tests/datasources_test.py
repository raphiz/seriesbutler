from seriesbutler import datasources
from seriesbutler.datasources import TheTvDb
from seriesbutler.models import DataSourceException
from unittest import mock
import datetime
from vcr import VCR
import responses
import requests
import pytest

vcr = VCR(cassette_library_dir='build/cassettes/datasources/')


@vcr.use_cassette()
def test_find_by_name_empty():
    datasource = TheTvDb()
    result = datasource.find_by_name('')
    assert 0 == len(result)


@vcr.use_cassette()
def test_find_by_name_None():
    datasource = TheTvDb()
    result = datasource.find_by_name(None)
    assert 0 == len(result)


@vcr.use_cassette()
def test_find_by_name_single_match():
    datasource = TheTvDb()
    result = datasource.find_by_name('Brooklyn Nine-Nine')
    assert 1 == len(result)

    assert 'Brooklyn Nine-Nine' == result[0][0]
    assert 'tt2467372' == result[0][1]


@vcr.use_cassette()
def test_find_by_name_multi_match():
    datasource = TheTvDb()
    result = datasource.find_by_name('Family')
    assert 10 == len(result)

    assert 'Family' == result[0][0]
    assert 'tt0073992' == result[0][1]


@vcr.use_cassette()
def test_episodes_for_series_without_tvdbid():
    datasource = TheTvDb()
    series = {'name': 'Person of interest', 'imdb': 'tt1839578',
              'start_from': {'season': 1, 'episode': 1}}

    result = datasource.episodes_for_series(series)

    # There are 94 episodes listed - but only 90 have a date when they
    # were aired for the first time
    assert series['tvdb'] == '248742'


@responses.activate
def test_find_by_name_server_error():
    # Prepare a fake server error response
    responses.add(responses.GET, 'http://thetvdb.com/api/GetSeries.php',
                  status=404)
    datasource = TheTvDb()

    # Ensure an exception is thrown
    with pytest.raises(DataSourceException) as exceptionInfo:
        result = datasource.find_by_name('Breaking')

    # Assert exception message
    assert str(exceptionInfo.value) == 'Failed search by name (server error)'


def test_episodes_for_series_with_None():
    datasource = TheTvDb()

    # Ensure an exception is thrown
    with pytest.raises(DataSourceException) as exceptionInfo:
        result = datasource.episodes_for_series(None)
    # Assert exception message
    assert str(exceptionInfo.value) == 'No Series configuration provided'


@vcr.use_cassette()
def test_episodes_for_series_happy_path():
    datasource = TheTvDb()
    series = {'name': 'Breaking Bad', 'imdb': 'tt0903747',
              'tvdb': '81189', 'start_from': {'season': 1, 'episode': 2}}
    result = datasource.episodes_for_series(series)

    assert len(result) == 62


@vcr.use_cassette('../../../tests/data/no_aired_date.yml')
def test_episodes_for_series_no_aired_date():
    datasource = TheTvDb()
    series = {'name': 'Person of interest', 'imdb': 'tt1839578',
              'tvdb': '248742', 'start_from': {'season': 1, 'episode': 1}}
    result = datasource.episodes_for_series(series)

    # There are 94 episodes listed - but only 90 have a date when they
    # were aired for the first time
    assert len(result) == 90


@vcr.use_cassette('../../../tests/data/not_aired_yet.yml')
def test_episodes_for_series_not_aired_yet(monkeyplus):

    datetime_patcher = mock.patch.object(
        datasources, 'datetime',
        mock.Mock(wraps=datetime.datetime)
    )
    mocked_datetime = datetime_patcher.start()
    mocked_datetime.now.return_value = datetime.datetime(2015, 4, 6)
    datasource = TheTvDb()
    series = {'name': 'Person of interest', 'imdb': 'tt1839578',
              'tvdb': '248742', 'start_from': {'season': 1, 'episode': 1}}
    result = datasource.episodes_for_series(series)
    datetime_patcher.stop()

    # There are 94 episodes listed - but only 86 of these episodes were
    # aired before 2015-04-06
    assert len(result) == 86


@vcr.use_cassette('../../../tests/data/skip_specials.yml')
def test_episodes_for_series_skip_specials():

    datasource = TheTvDb()
    series = {'name': 'Last Week Tonight with John Oliver', 'tvdb': '278518',
              'imdb': 'tt3530232', 'start_from': {'season': 1, 'episode': 1}}
    result = datasource.episodes_for_series(series)

    assert len(result) == 50


@vcr.use_cassette()
def test_episodes_for_series_without_tvdbid_invalid_imdb_id():
    datasource = TheTvDb()
    series = {'name': '?', 'imdb': 'tt3530002',
              'start_from': {'season': 1, 'episode': 1}}

    # Ensure an exception is thrown
    with pytest.raises(DataSourceException) as exceptionInfo:
        result = datasource.episodes_for_series(series)

    # Assert exception message
    assert str(exceptionInfo.value) == ('Failed to recieve tvdb id: '
                                        'No unique match!')


@responses.activate
def test_episodes_for_series_server_error():
    # Prepare a fake server error response
    responses.add(responses.GET, 'http://thetvdb.com/api/'
                  'GetSeriesByRemoteID.php', status=404)

    datasource = TheTvDb()
    series = {'name': 'Last Week Tonight with John Oliver',
              'imdb': 'tt3530232', 'start_from': {'season': 1, 'episode': 1}}

    # Ensure an exception is thrown
    with pytest.raises(DataSourceException) as exceptionInfo:
        result = datasource.episodes_for_series(series)

    # Assert exception message
    assert str(exceptionInfo.value) == 'Failed to fetch tvdb id (server error)'
