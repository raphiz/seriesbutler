from seriesbutler.providers import Solarmovie, WatchTvSeries, PutlockerSeries
from seriesbutler.datasources import TheTvDb
from vcr import VCR
import responses
import pytest
import os

vcr = VCR(cassette_library_dir=os.path.join(
    os.getcwd(), 'build/cassettes/datasources/'))


@pytest.mark.parametrize("provider", [Solarmovie(), WatchTvSeries(),
                         PutlockerSeries()])
@vcr.use_cassette(record_mode='new_episodes')
def test_links_for_not_existing(provider):
    series = {'name': 'invalid', 'imdb': 'tt99'}
    assert len(provider.links_for(series, 1, 1)) == 0


@pytest.mark.parametrize("provider", [Solarmovie(), WatchTvSeries(),
                         PutlockerSeries()])
@vcr.use_cassette(record_mode='new_episodes')
def test_links_for_invalid_episode(provider):
    series = {'name': 'Breaking Bad', 'imdb': 'tt0903747'}
    assert len(provider.links_for(series, 9, 9)) == 0


@pytest.mark.parametrize("provider", [Solarmovie(), WatchTvSeries()
                         PutlockerSeries()])
@vcr.use_cassette(record_mode='new_episodes')
def test_links_happy_path(provider):
    series = {'name': 'Breaking Bad', 'imdb': 'tt0903747'}
    assert len(provider.links_for(series, 4, 4)) > 10


@vcr.use_cassette(record_mode='once')
def test_links_for_putlockerSeries():
    provider = PutlockerSeries()
    series = {'name': 'Shameless (US)', 'imdb': 'tt1586680'}
    results = provider.links_for(series, 5, 5)
    print(results[0].direct())


@responses.activate
def test_solarmovie_links_network_error():
    # Prepare fake server error responses
    responses.add(responses.GET, 'https://www.solarmovie.ph/suggest-movie/',
                  status=200, body='[{"id":70962,"value":"0903747","label":'
                  '"Breaking Bad","url":"\/tv\/breaking-bad-2008\/","year":'
                  '2008,"release":"2008-01-20","tv":true,"episode":false}]')
    responses.add(responses.GET, 'https://www.solarmovie.ph/tv/'
                  'breaking-bad-2008/season-4/episode-4/', status=500)

    series = {'name': 'Breaking Bad', 'imdb': 'tt0903747'}
    provider = Solarmovie()

    assert 0 == len(provider.links_for(series, 4, 4))


@responses.activate
def test_solarmovie_links_suggest_network_error():
    # Prepare fake server error responses
    responses.add(responses.GET, 'https://www.solarmovie.ph/suggest-movie/',
                  status=500)

    series = {'name': 'Breaking Bad', 'imdb': 'tt0903747'}
    provider = Solarmovie()

    assert 0 == len(provider.links_for(series, 4, 4))


@pytest.mark.parametrize("provider, link, expected", [
    (Solarmovie(), 'https://www.solarmovie.ph/link/play/4967257/',
        'http://vodlocker.com/cnmg1ihv0765'),
    (Solarmovie(), 'http://www.solarmovie.ph/link/play/5018874/',
        'http://www.thevideo.me/61mbhoxagcny'),
    (WatchTvSeries(), 'http://thewatchseries.to/open/cale/1758021.html',
        'http://daclips.in/iq999atdu5qk'),
    (WatchTvSeries(), 'http://thewatchseries.to/cale.html?'
        'r=aHR0cDovL2dvcmlsbGF2aWQuaW4veHZmZ2NhOGpjenI2',
        'http://gorillavid.in/xvfgca8jczr6')

])
@vcr.use_cassette(record_mode='new_episodes')
def test_unwrap(provider, link, expected):
    assert expected == provider.unwrap(link)


@responses.activate
@pytest.mark.parametrize("provider, link", [
    (Solarmovie(), "https://www.solarmovie.ph/link/play/4967257/"),
    (WatchTvSeries(), "http://thewatchseries.to/open/cale/1758021.html")
])
def test_unwrap_network_error(provider, link):
    # Prepare fake server error response
    responses.add(responses.GET, link, status=500)
    assert provider.unwrap(link) is None
