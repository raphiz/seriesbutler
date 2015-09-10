import requests
from xml.etree import ElementTree
import logging
from datetime import datetime
from .models import DataSourceException
logger = logging.getLogger(__name__)


class TheTvDb(object):

    base = 'http://thetvdb.com/api/'
    api_key = 'A5DEEF1D77DAD6F3'
    cache = {}

    def _format_url(self, tmpl, **kwargs):
        return tmpl.format(base=self.base, api_key=self.api_key, **kwargs)

    def find_by_name(self, name):
        if name is None:
            return []

        response = requests.get(self._format_url(
            '{base}GetSeries.php?seriesname={name}', name=name))

        if not response.ok:
            logger.error("Status code {0} ({1})!".format(
                response.status_code, response.url))
            raise DataSourceException("Failed search by name (server error)")

        root = ElementTree.fromstring(response.content)
        result = []
        for series_elm in root.findall('./Series'):
            series_name = series_elm.find('SeriesName')
            series_imdbid = series_elm.find('IMDB_ID')
            if series_name is not None and series_imdbid is not None:
                result.append((
                    series_name.text,
                    series_imdbid.text
                ))
        return result

    def _get_tvdb_id(self, series):
        response = requests.get(self._format_url(
            '{base}GetSeriesByRemoteID.php?imdbid={imdb_id}',
            imdb_id=series['imdb']))

        if not response.ok:
            logger.error("Response is not OK!")
            raise DataSourceException("Failed to fetch tvdb id (server error)")

        root = ElementTree.fromstring(response.content)
        names = root.findall('./Series/seriesid')
        if len(names) is not 1:
            logger.error('No unique match found for imdb ' + series['imdb'])
            raise DataSourceException("Failed to recieve tvdb id: "
                                      "No unique match!")

        tvdbid = root.findall('./Series/seriesid')[0].text
        return tvdbid

    def episodes_for_series(self, series):
        if series is None:
            raise DataSourceException("No Series configuration provided")

        if 'tvdb' not in series.keys():
            series['tvdb'] = self._get_tvdb_id(series)

        seriesid = series['tvdb']
        response = requests.get(self._format_url(
            '{base}/{api_key}/series/{seriesid}/all/en.xml', seriesid=seriesid
        ))
        root = ElementTree.fromstring(response.content)
        episodes = []
        for xml_episode in root.findall('./Episode'):
            season = int(xml_episode.find('SeasonNumber').text)
            episode = int(xml_episode.find('EpisodeNumber').text)
            # Skip "Specials"
            if season < 1:
                continue

            # Skip If not yet released...
            try:
                first_aired = datetime.strptime(
                    xml_episode.find('FirstAired').text,
                    "%Y-%m-%d")
            except TypeError:
                logger.debug('Skipping episode s{0}e{1} - has no FirstAired'
                             'attribute'.format(season, episode))
                continue
            if datetime.now() < first_aired:
                logger.debug('Skipping episode s{0}e{1} - is in the future'
                             .format(season, episode))
                continue

            episodes.append((season, episode))
        return episodes
