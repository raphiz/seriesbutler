from bs4 import BeautifulSoup
import requests
import re
from .models import Link
import logging

logger = logging.getLogger(__name__)


class WatchTvSeries(object):

    base = 'http://watchseries.ag'

    def links_for(self, episode):
        name = episode.series.name.replace(' ', '_')
        result = []

        r = requests.get(
            "{0}/episode/{1}_s{2}_e{3}.html".
            format(self.base, name, episode.season_no, episode.episode_no))
        if r.status_code != 200:
            logger.warn("WatchTvSeries has no links for {0} ({1})!"
                        .format(episode.series.name, episode))
            return result

        soup = BeautifulSoup(r.text)
        for elm in soup.select('#lang_1 .myTable tr'):
            link = self.base + list(elm.children)[1].a['href']
            hoster = list(elm.children)[0].span.string.strip()
            result.append(Link(link, hoster, self.unwrap))
        return result

    def unwrap(self, link):
        r = requests.get(link)
        if r.status_code != 200:
            logger.error("Status code {0} ({1})!".format(r.status_code, r.url))
            return None

        soup = BeautifulSoup(r.text)
        direct = soup.select('.myButton')[0]['href']

        return direct


class Solarmovie(object):

    base = 'https://www.solarmovie.is'

    def links_for(self, episode):
        name = self._uniqe_name(episode.series.imdb_id)
        result = []
        if not name:
            return result

        r = requests.get(
            "{0}/{1}/season-{2}/episode-{3}/".
            format(self.base, name, episode.season_no, episode.episode_no))
        if r.status_code != 200:
            logger.warn("Solarmovie has no links for {0} ({1})!"
                        .format(episode.series.name, episode))
            return result

        soup = BeautifulSoup(r.text)
        for elm in soup.select('.dataTable tbody tr'):
            # Skip promoted links
            if not elm.has_attr('id'):
                continue
            link = 'http://solarmovie.is/link/play/{0}/'.format(elm['id'][5:])
            hoster = elm.a.string.strip()
            result.append(Link(link, hoster, self.unwrap))
        return result

    def unwrap(self, link):
        r = requests.get(link)
        if r.status_code != 200:
            logger.error("Status code {0} ({1})!".format(r.status_code, r.url))
            return None

        soup = BeautifulSoup(r.text)
        direct = soup.select('iframe')[0]['src']

        # Special handling for embedded...
        match = re.fullmatch(
            '(http|https)\:\/\/([^\/]*)\/embed-([^-]*)-[0-9]*x[0-9]*.html',
            direct)
        if match:
            return '{0}://{1}/{2}'.format(*match.groups())
        return direct

    def _uniqe_name(self, imdb_id):
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
        }

        r = requests.get(
            '{0}/suggest-movie/?tv=all&term={1}'.
            format(self.base, imdb_id[2:]),
            headers=headers
        )

        if r.status_code != 200:
            logger.error("Status code {0} ({1})!".format(r.status_code, r.url))
            return None

        result = r.json()
        if len(result) != 1:
            logger.error(
                "Could not find seris with imdb_id %s: {0}"
                .format(imdb_id)
            )
            return None
        return result[0]['url']
