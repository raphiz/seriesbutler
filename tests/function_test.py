from seriesbutler import functions
from seriesbutler.models import SeriesbutlerException
from seriesbutler.models import ConfigurationException, Link
from unittest.mock import MagicMock
import pytest
import os


# def test_init():
# TODO! (also cli test!)
#   pass


def test_load_configuration_invalid_cfg():
    with pytest.raises(ConfigurationException) as exceptionInfo:
        functions.load_configuration('tests/data/examples/invalid')
    assert (str(exceptionInfo.value) == 'series.0.start_from.season -> '
            '-1 is less than the minimum of 0')


def test_load_configuration_invalid_cfg():
    with pytest.raises(ConfigurationException) as exceptionInfo:
        functions.load_configuration('tests/data/examples/invalid')
    assert (str(exceptionInfo.value) == 'series.0.start_from.season -> '
            '-1 is less than the minimum of 0')


def test_load_configuration_missing_cfg():
    with pytest.raises(FileNotFoundError) as exceptionInfo:
        functions.load_configuration('tests/data/examples/missing')


def test_load_configuration_without_working_directory():
    # Switch working directory
    with functions._pushd('tests/data/examples/valid'):
        cfg = functions.load_configuration()
        assert cfg['working_directory'].endswith('tests/data/examples/valid')


def test_load_configuration_happy_path():
    cfg = functions.load_configuration('tests/data/examples/valid')

    # Assert loaded values (some samples)
    assert len(cfg['hosters']['ignored']) == 1
    assert len(cfg['hosters']['prefered']) == 1
    assert cfg['series'][0]['imdb'] == 'tt2467372'
    assert cfg['series'][0]['name'] == 'Brooklyn Nine-Nine'
    assert cfg['series'][0]['tvdb'] == '269586'

    # Asset dynamic properties
    assert cfg['working_directory'].endswith('tests/data/examples/valid')
    assert cfg['config_path'].endswith('examples/valid/seriesbutler.json')


@pytest.fixture
def config(tmpdir):
    return {
        "hosters": {
            "ignored": [],
            "prefered": []
        },
        "working_directory": tmpdir.strpath,
        "config_path": tmpdir.join('seriesbutler.json').strpath,
        "series": []
    }


@pytest.fixture
def series(tmpdir):
    return {
        "imdb": "tt2467372",
        "name": "Brooklyn Nine-Nine",
        "start_from": {"episode": 4, "season": 1}
    }


def test_save_configuration_missig_dynamic_properties(monkeypatch, config):
    monkeypatch.delitem(config, 'working_directory')
    monkeypatch.delitem(config, 'config_path')
    with pytest.raises(ConfigurationException) as exceptionInfo:
        functions.save_configuration(config)

    assert (str(exceptionInfo.value) == 'Missing dynamic properties'
            '(working_directory and/or config_path)')


def test_save_configuration_with_invalid_cfg(monkeypatch, config):
    monkeypatch.delitem(config, 'hosters')

    with pytest.raises(ConfigurationException) as exceptionInfo:
        functions.save_configuration(config)

    assert (str(exceptionInfo.value) ==
            ' -> \'hosters\' is a required property')


def test_save_configuration_happy_path(config):
    functions.save_configuration(config)
    assert len(open(config['config_path']).read()) == 90


def test_remove_series_with_non_existing_series(series, config):
    with pytest.raises(SeriesbutlerException) as exceptionInfo:
        functions.remove_series(config, series)

    assert (str(exceptionInfo.value) == 'The given series is not registered '
            'in the given configuration!')


def test_remove_series_with_non_existing_series_directory(series, config):
    config['series'].append(series)

    functions.remove_series(config, series)

    assert len(config['series']) == 0


def test_remove_series_happy_path(series, config):
    config['series'].append(series)

    # Create a directory for the series...
    os.mkdir(os.path.join(config['working_directory'], 'Brooklyn Nine-Nine'))

    functions.remove_series(config, series)

    assert len(config['series']) == 0
    assert len(open(config['config_path']).read()) == 90


def test_add_series_series_already_exists(config, series):
    config['series'].append(series)
    with pytest.raises(SeriesbutlerException) as exceptionInfo:
        functions.add_series(config, series)

    assert (str(exceptionInfo.value) == 'Series with imdbid tt2467372 is '
            'already registered!')


def test_add_series_directory_already_exists(config, series):

    os.mkdir(os.path.join(config['working_directory'], series['name']))
    functions.add_series(config, series)
    assert os.path.exists(os.path.join(config['working_directory'],
                          series['name']))


def test_add_series_happy_path(config, series):
    assert series not in config['series']

    functions.add_series(config, series)

    assert series in config['series']
    assert os.path.exists(os.path.join(config['working_directory'],
                          series['name']))

    assert len(open(config['config_path']).read()) == 290


def test_fetch_all_called_with_invalid_series_cfg(monkeypatch, config, series):
    monkeypatch.delitem(series, 'start_from')
    with pytest.raises(ConfigurationException) as exceptionInfo:
        functions.add_series(config, series)


def test_fetch_all_happy_path(mocker, config, series):
    mocker.patch('seriesbutler.functions.fetch_series')
    config['series'].append(series)
    functions.fetch_all(config, [], None)

    # Just assert that the fetch_series method is called for each series
    functions.fetch_series.assert_called_once_with(config, series, [], None)


def test_fetch_series_series_not_in_cfg(config, series):
    with pytest.raises(SeriesbutlerException) as exceptionInfo:
        functions.fetch_series(config, series, [], None)

    assert (str(exceptionInfo.value) == 'The given series is not registered '
            'in the given configuration!')


def test_fetch_series_no_links_found(mocker, config, series):
    config['series'].append(series)

    mock_datasource = MagicMock()
    mock_datasource.episodes_for_series.return_value = [(1, 1), (1, 2), (1, 3),
                                                        (1, 4), (1, 5), (1, 6)]
    # Patch the logger
    mocker.patch('seriesbutler.functions.logger.error')

    functions.fetch_series(config, series, [], mock_datasource)

    # assert the fact that there were no links found got reported
    assert functions.logger.error.call_count == 2
    functions.logger.error.assert_any_call('Could not download Brooklyn Nine-'
                                           'Nine s1e5. No working links found')
    functions.logger.error.assert_any_call('Could not download Brooklyn Nine-'
                                           'Nine s1e6. No working links found')


def test_fetch_series_download_fails(mocker, config, series):
    config['series'].append(series)

    # Mock a datasource
    mock_datasource = MagicMock()
    mock_datasource.episodes_for_series.return_value = [(1, 1), (1, 2), (1, 3),
                                                        (1, 4), (1, 5)]
    # Mock a provider
    mock_provider = MagicMock()
    mock_provider.links_for.return_value = [Link('U', 'P', lambda x: '://'+x)]

    # Patch the download method
    mocker.patch('seriesbutler.functions.download')
    functions.download.return_value = False

    # Patch the logger
    mocker.patch('seriesbutler.functions.logger.error')

    # Call the fetch method
    functions.fetch_series(config, series, [mock_provider], mock_datasource)

    # Verify that the error messages were logged
    functions.logger.error.assert_any_call('Failed to download Brooklyn Nine-'
                                           'Nine s1e5')

    functions.logger.error.assert_any_call('Could not download Brooklyn Nine-'
                                           'Nine s1e5. No working links found')


def test_fetch_series_happy_path(mocker, config, series):
    config['series'].append(series)

    # Mock a datasource
    mock_datasource = MagicMock()
    mock_datasource.episodes_for_series.return_value = [(1, 1), (1, 2), (1, 3),
                                                        (1, 4), (1, 5)]
    # Mock a provider
    mock_provider = MagicMock()
    mock_provider.links_for.return_value = [Link('U', 'P', lambda x: '://'+x)]

    # Patch the download method
    mocker.patch('seriesbutler.functions.download')
    functions.download.return_value = True

    # Call the fetch method
    functions.fetch_series(config, series, [mock_provider], mock_datasource)

    # Verify the download method was called properly
    functions.download.assert_called_once_with('://U', os.path.join(
        config['working_directory'], series['name']), 's01e05')

    # Verify that the start_from value has been updated
    assert config['series'][0]['start_from']['episode'] == 5
    assert config['series'][0]['start_from']['season'] == 1


# TODO Tests for download
# Called with valid link (happy path)
# Called with invalid link
# Called with nonexisting dir
# Called with existing filename
