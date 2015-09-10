from bs4 import BeautifulSoup
import requests
import re
from .models import Link
import logging

logger = logging.getLogger(__name__)


class WatchTvSeries(object):

    base = 'http://watchseries.ag'

    def links_for(self, series, season, episode):
        result = []

        name_in_url = series['name'].replace(' ', '_')
        response = requests.get(
            "{0}/episode/{1}_s{2}_e{3}.html"
            .format(self.base, name_in_url, season, episode))

        if not response.ok:
            logger.warn("WatchTvSeries has no links for {0} s{1}e{2}!"
                        .format(series['name'], season, episode))
            return result

        soup = BeautifulSoup(response.text, "html.parser")
        for element in soup.select('#lang_1 .myTable tr'):
            link = self.base + list(element.children)[1].a['href']
            hoster = list(element.children)[0].span.string.strip()
            result.append(Link(link, hoster, self.unwrap))
        return result

    def unwrap(self, link):
        response = requests.get(link)
        if not response.ok:
            logger.error("Failed to unwrap link {0} (Server error)!"
                         .format(link))
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        return soup.select('.myButton')[0]['href']


class Solarmovie(object):

    base = 'https://www.solarmovie.is'

    def links_for(self, series, season, episode):
        result = []

        # Fetch the name which is in the URL and abort if not found
        name_in_url = self._uniqe_name(series['imdb'])
        if not name_in_url:
            return result

        response = requests.get(
            "{0}{1}season-{2}/episode-{3}/".
            format(self.base, name_in_url, season, episode))

        if not response.ok:
            logger.warn("Solarmovie has no links for {0} (s{1}e{2})!"
                        .format(series['name'], season, episode))
            return result

        soup = BeautifulSoup(response.text, "html.parser")
        for elm in soup.select('.dataTable tbody tr'):
            # Skip promoted links
            if not elm.has_attr('id'):
                continue
            link = '{0}/link/play/{1}/'.format(self.base, elm['id'][5:])
            hoster = elm.a.string.strip()
            result.append(Link(link, hoster, self.unwrap))
        return result

    def unwrap(self, link):
        response = requests.get(link)
        if not response.ok:
            logger.error("Failed to unwrap link {0} (Server error)!"
                         .format(link))
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        direct = soup.select('iframe')[0]['src']

        # Special handling for embedded...
        match = re.fullmatch(
            '(http|https)\:\/\/([^\/]*)\/embed-([^-]*)-[0-9]*x[0-9]*.html',
            direct)
        if match:
            return '{0}://{1}/{2}'.format(*match.groups())
        return direct

    def _uniqe_name(self, imdb_id):
        response = requests.get(
            '{0}/suggest-movie/?tv=all&term={1}'.
            format(self.base, imdb_id[2:]),
            headers={'X-Requested-With': 'XMLHttpRequest'})

        if not response.ok:
            logger.error("Failed to solarmovie url identifier (Server error)")
            return None

        result = response.json()
        if len(result) != 1:
            logger.error(
                "Could not find series {0} on solarmovie".format(imdb_id))
            return None
        return result[0]['url']
