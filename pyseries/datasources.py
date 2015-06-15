import requests
from xml.etree import ElementTree
import logging
from datetime import datetime
logger = logging.getLogger(__name__)


class TheTvDb(object):

    base = 'http://thetvdb.com/api/'
    api_key = 'A5DEEF1D77DAD6F3'
    cache = {}

    def _format_url(self, tmpl, **kwargs):
        return tmpl.format(base=self.base, api_key=self.api_key, **kwargs)

    def _query_by_imdb(self, imdb_id):
        response = requests.get(self._format_url(
            '{base}GetSeriesByRemoteID.php?imdbid={imdb_id}', imdb_id=imdb_id))

        if response.status_code is not 200:
            logger.error("Status code {0} ({1})!".format(r.status_code, r.url))
            return imdb_id

        root = ElementTree.fromstring(response.content)
        names = root.findall('./Series/SeriesName')
        if len(names) is not 1:
            logger.info('No unique match found for imdb {0}'.format(imdb_id))
            return imdb_id
        seriesid = root.findall('./Series/seriesid')[0].text
        self.cache[imdb_id] = {'name': names[0].text, 'seriesid': seriesid}
        return names[0].text

    def name_for_imdb_id(self, imdb_id):
        if imdb_id in self.cache.keys():
            return self.cache[imdb_id]['name']
        return self._query_by_imdb(imdb_id)

    def episodes_for_imdb_id(self, imdb_id):
        if imdb_id not in self.cache.keys():
            self.name_for_imdb_id(imdb_id)
        seriesid = self.cache[imdb_id]['seriesid']
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
            first_aired = datetime.strptime(
                xml_episode.find('FirstAired').text,
                "%Y-%m-%d"
            )
            if datetime.now() < first_aired:
                continue

            episodes.append((season, episode))
        return episodes