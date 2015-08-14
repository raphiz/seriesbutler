import logging
logger = logging.getLogger(__name__)


class Link(object):

    def __init__(self, url, hoster, unwrap):
        self.url = url
        self.hoster = hoster
        self.unwrap = unwrap

    def direct(self):
        return self.unwrap(self.url)


class Configuration(object):
    path = None
    ini_file = None
    from_season = None
    from_episode = None
    prefered_hosters = None
    ignored_hosters = None
    link_providers = None
    datasource = None

    def __setattr__(self, name, value):
        if hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            raise TypeError('Cannot set configuration property {0}'
                            .format(name))


class Series(object):
    def __init__(self, name, imdb_id, configuration):
        self.name = name
        self.imdb_id = imdb_id
        self.configuration = configuration

    def episodes(self):
        episodes = []
        eps = self.configuration.datasource.episodes_for_imdb_id(self.imdb_id)
        for season, episode in eps:
            episodes.append(
                Episode(self, season, episode))
        return episodes

    def __repr__(self):
        return "{0} ({1})".format(self.name, self.imdb_id)


class Episode(object):
    def __init__(self, series, season_no, episode_no):
        self.series = series
        self.season_no = season_no
        self.episode_no = episode_no

    def links(self):
        links = []
        for provider in self.series.configuration.link_providers:
            links += provider.links_for(self)
        return self.sort(links)

    def sort(self, links):
        prefered = []
        others = []

        for link in links:
            if self.__in_hoster(link.hoster,
               self.series.configuration.prefered_hosters):
                prefered.append(link)
                continue
            if not self.__in_hoster(link.hoster,
               self.series.configuration.ignored_hosters):
                others.append(link)
        logger.info("Found {0} prefered links for {1}"
                    .format(len(prefered), self))
        return prefered + others

    def __in_hoster(self, link_hoster, list):
        for declared_hoster in list:
            if link_hoster.startswith(declared_hoster):
                return True
        return False

    def __lt__(self, other):
        if self.season_no < other.season_no:
            return True
        if self.season_no is other.season_no \
           and self.episode_no < other.episode_no:
            return True
        return False

    def __gt__(self, other):
        if self.season_no > other.season_no:
            return True
        if self.season_no is other.season_no \
           and self.episode_no > other.episode_no:
            return True
        return False

    def __eq__(self, other):
        return self.season_no is other.season_no \
            and self.episode_no is other.episode_no

    def __str__(self):
        return '{0} s{1}e{2}'.format(
            self.series.name,
            self.season_no,
            self.episode_no
        )

    def __repr__(self):
        return '"{0}" - "s{1}e{2}'.format(
            self.series.name,
            self.season_no,
            self.episode_no
        )
