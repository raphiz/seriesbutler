import os
import json
import shutil
import youtube_dl
import logging
import logging.config
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from contextlib import contextmanager
from .models import ConfigurationException, SeriesbutlerException
from .models import configuration_schema

logger = logging.getLogger(__name__)


def load_configuration(working_directory=None):
    working_directory = _get_working_directory(working_directory)
    config_path = _get_config_path(working_directory)

    logger.info('Working directory is {0}'.format(working_directory))

    try:
        with open(config_path, 'r') as fp:
            cfg = json.load(fp)
            validate(cfg, configuration_schema)

            cfg['working_directory'] = working_directory
            cfg['config_path'] = config_path
            return cfg
    except ValidationError as e:
        raise ConfigurationException(
            '{0} -> {1}'.format('.'.join(str(i) for i in e.path), e.message))
    except Exception as e:
        raise e


def save_configuration(configuration):
    copy = configuration.copy()

    if not ('working_directory' in configuration.keys() and
            'config_path' in configuration.keys()):
        raise ConfigurationException('Missing dynamic properties'
                                     '(working_directory and/or config_path)')
    # Clear temporary configuration
    copy.pop('working_directory')
    copy.pop('config_path')

    # validate
    try:
        validate(copy, configuration_schema)
    except ValidationError as e:
        raise ConfigurationException(
            '{0} -> {1}'.format('.'.join(str(i) for i in e.path), e.message))

    with open(configuration['config_path'], 'w+') as fp:
        json.dump(copy, fp, sort_keys=True, indent=4, separators=(',', ': '))


def _get_working_directory(working_directory):
    if working_directory is None:
        return os.getcwd()
    return os.path.abspath(working_directory)


def _get_config_path(working_directory):
    return os.path.join(working_directory, 'seriesbutler.json')


def init(working_directory):
    working_directory = _get_working_directory(working_directory)

    if not os.path.isdir(working_directory):
        raise SeriesbutlerException('"{0}" is not a directory!'.format(
                                    working_directory))
    if len(os.listdir(working_directory)) > 0:
        raise SeriesbutlerException('"{0}" is not empty!'.format(
                                    working_directory))
    config_path = _get_config_path(working_directory)

    configuration = {
        'working_directory': working_directory,
        'config_path': config_path,
        "hosters": {"ignored": [], "prefered": []},
        'series': []
    }

    save_configuration(configuration)


def remove_series(configuration, series_configuration):
    if series_configuration not in configuration['series']:
        raise SeriesbutlerException('The given series is not registered in the'
                                    ' given configuration!')

    # Remove the directory that contains all series
    series_directory = os.path.join(configuration['working_directory'],
                                    series_configuration['name'])
    if os.path.exists(series_directory):
        shutil.rmtree(series_directory)

    # Remove the entry from the configuration
    configuration['series'].remove(series_configuration)
    save_configuration(configuration)


def add_series(configuration, series):
    # Check if the given series is already registered
    for existing in configuration['series']:
        if existing['imdb'] == series['imdb']:
            raise SeriesbutlerException('Series with imdbid {0} is already '
                                        'registered!'.format(series['imdb']))

    # Add series to the configuration and save it
    configuration['series'].append(series)
    save_configuration(configuration)

    # Create the directory to store the files in
    dst = os.path.join(configuration['working_directory'], series['name'])
    if not os.path.exists(dst):
        os.mkdir(dst)
    return series


def fetch_all(configuration, link_providers, datasource):
    for series in configuration['series']:
        fetch_series(configuration, series, link_providers, datasource)


def fetch_series(configuration, series, link_providers, datasource):
    if series not in configuration['series']:
        raise SeriesbutlerException('The given series is not registered in the'
                                    ' given configuration!')
    episodes = datasource.episodes_for_series(series)

    # Remove watched episodes
    episodes = _remove_ignored(series, episodes)

    succeeded = False
    for episode in episodes:
        # Try to download the links - they are already sorted
        for link in _links_for_episode(episode, series, configuration,
                                       link_providers):
            succeeded = download(
                link.direct(),
                os.path.join(configuration['working_directory'],
                             series['name']),
                's{0}e{1}'.format(episode[0], episode[1]))
            if succeeded:
                # Update start from & save it
                series['start_from']['season'] = episode[0]
                series['start_from']['episode'] = episode[1]
                save_configuration(configuration)

                logger.info("Downloaded {0} s{1}e{2}".format(
                    series['name'], episode[0], episode[1]))
                break
            else:
                logger.error("Failed to download {0} s{1}e{2}".format(
                    series['name'], episode[0], episode[1]))
        if not succeeded:
            logger.error("Could not download {0} s{1}e{2}. No working links "
                         "found".format(
                             series['name'], episode[0], episode[1]))


def download(direct, series_directory, filename):
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
        with _pushd(series_directory):
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([direct])

        return True

    except Exception as e:
        logger.info(
            'Failed to download from link {0} - {1}'.format(direct, e)
        )
    return False


def _remove_ignored(series, episodes):
    """
    Removes all episodes from the given episodes list that the user has
    already watched
    """
    def fn(one, two):
        if one[0] < two[0]:
            return True
        if one[0] == two[0] and one[1] < two[1]:
            return True
        return False

    from_episode = (series['start_from']['season'],
                    series['start_from']['episode'])
    return list(filter(lambda e: fn(from_episode, e), episodes))


def _links_for_episode(episode, series, configuration, link_providers):
    # Fetch all links from the providers
    links = []
    for provider in link_providers:
        links += provider.links_for(series, episode[0], episode[1])

    #  Sort them so that the prefered ones are on top
    prefered = []
    others = []

    for link in links:
        if _in_hoster(link.hoster,
           configuration['hosters']['prefered']):
            prefered.append(link)
            continue
        if not _in_hoster(link.hoster,
           configuration['hosters']['ignored']):
            others.append(link)
    logger.info("Found {0} prefered links for {1} s{2}e{3}"
                .format(len(prefered), series['name'], episode[0], episode[1]))
    return prefered + others


def _in_hoster(link_hoster, list):
    for declared_hoster in list:
        if link_hoster.startswith(declared_hoster):
            return True
    return False


def _has_suitable_extractor(url):
    """
    Tests wheater youtube-dl has a suitable extractor for the given
    url. If so, returns true, otherwise false.
    The "generic" extractor is ingored.
    """
    for extractor in youtube_dl.list_extractors(18):
        if extractor.suitable(url):
            # Skip the generic downloader
            if(extractor.IE_NAME == 'generic'):
                continue
            return True
    return False


@contextmanager
def _pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)


def _setup_logging(log_level):
    """
        Setup logging configuration
    """
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '[%(asctime)s] [%(levelname)-7s]: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            },
        },
        'loggers': {
            '': {
                'level': log_level,
                'handlers': ['console']
            },
            'requests': {
                'level': 'WARNING',
                'handlers': ['console']
            }
        }
    })
