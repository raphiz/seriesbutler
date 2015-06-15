from .models import Series, Configuration, Episode
import os
import re
import youtube_dl
from configobj import ConfigObj
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def download(direct, working_directory, filename):
    """
    Download the given url into a file called filename.ext where ext is the
    extension of the videos file format.
    This method returns true if the download was succesful.
    """
    try:
        if not _has_suitable_extractor(direct):
            logger.info(
                'No suitable extractor forund for url {0}'.format(direct)
            )
            return False

        logger.info("Downloading from ... {0}".format(direct))
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename + '.%(ext)s'
        }
        with pushd(working_directory):
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([direct])

        return True

    except Exception as e:
        logger.info(
            'Failed to download from link {0}'.format(direct)
        )
    return False


def remove_ignored(series, episodes):
    from_episode = Episode(series, series.configuration.from_season,
                           series.configuration.from_episode - 1)
    return filter(lambda e: from_episode < e, episodes)


def load_series(working_directory, link_providers, datasource):
    """
    Loads all series from the given working_directory and returns a list
    containing valid series models.
    """
    logger.info('Working directory is {0}'.format(working_directory))
    series = []
    prefered_hosters = []
    ignored_hosters = []

    global_cfg_path = os.path.join(working_directory, 'pyseries.ini')
    if os.path.exists(global_cfg_path):
        global_cfg = ConfigObj(global_cfg_path, list_values=False)
        if global_cfg.get('prefered_hosters'):
            prefered_hosters = global_cfg.get('prefered_hosters').split(',')
        if global_cfg.get('ignored_hosters'):
            ignored_hosters = global_cfg.get('ignored_hosters').split(',')

    # For each file in the root directory
    for value in os.listdir(working_directory):
        #  If the current file is a directory and contains a file called
        # info.ini

        cfg = Configuration()
        cfg.path = os.path.join(working_directory, value)
        cfg.ini_file = os.path.join(cfg.path, 'info.ini')

        # Skip files and folders withou an info.ini file...
        if not (os.path.isdir(cfg.path) and os.path.isfile(cfg.ini_file)):
            logger.info(
                'Skipping file/folder "{0}"'
                .format(value)
            )
            continue

        ini = ConfigObj(cfg.ini_file)

        # Skip if the conifg is invalid...
        if _is_valid_ini(ini, cfg.ini_file) is False:
                continue

        logger.info('Investigating into folder "{0}"...'.format(value))

        imdb_id = ini.get('imdb')
        cfg.from_season, cfg.from_episode = _start_from(cfg.path, ini)
        cfg.prefered_hosters = prefered_hosters
        cfg.ignored_hosters = ignored_hosters
        cfg.link_providers = link_providers
        cfg.datasource = datasource

        name = datasource.name_for_imdb_id(imdb_id)
        series.append(Series(name, imdb_id, cfg))

    return series


def _start_from(path, config):
    """
    Returns a tuple from_season, from_episode - where to start to download
    the episodes from. This is ether from the config or from a file within the
    given path.
    """
    from_season = int(config.get('from_season') or 0)
    from_episode = int(config.get('from_episode') or 0)

    for filename in os.listdir(path):
        match = re.fullmatch('s([0-9]*)e([0-9]*)\..*', filename)
        if not match:
            continue

        season = int(match.group(1))
        episode = int(match.group(2))+1

        if from_season < season \
           or (from_season == season and from_episode < episode):
            from_season = season
            from_episode = episode
            logger.info(
                "Starting from season {0} episode {1} (from FS) - {2}"
                .format(from_season, from_episode, config.get('imdb'))
            )
    return from_season, from_episode


def _has_suitable_extractor(url):
    """
    Tests wheater youtube-dl has a suitable extractor for the given
    url. If so, returns true, otherwise false.
    The "generic" extractor is ingored.
    """
    for extractor in youtube_dl.extractor.list_extractors(18):
        if extractor.suitable(url):
            # Skip the generic downloader
            if(extractor.IE_NAME == 'generic'):
                continue
            return True
    return False


def _is_valid_ini(config, path):
    if config.get('imdb') is None:
        return False
    if config.get('imdb')[:2] != 'tt':
        logger.warn(
            'Please add the tt prefix from the imdb link in {0}!'.format(path)
        )
        return False
    return True


@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)
