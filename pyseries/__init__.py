from .functions import download, remove_ignored, load_series
from .providers import Solarmovie, WatchTvSeries
from .datasources import TheTvDb
import logging.config
import logging
import json
import sys
import os

logger = logging.getLogger(__name__)
__version__ = "0.0.4"


def setup_logging(default_path='logging.json',
                  default_level=logging.INFO,
                  env_key='LOG_CFG'):
    """
        Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    #  Mute requests
    logging.getLogger("requests").setLevel(logging.WARNING)


def main(working_directory):
    # Define, which link providers and datasources shall be used
    link_providers = [Solarmovie(), WatchTvSeries()]
    datasource = TheTvDb()

    for series in load_series(working_directory, link_providers, datasource):

        episodes = series.episodes()

        # Remove the episodes that are ignored - or
        episodes = remove_ignored(series, episodes)

        for episode in episodes:
            # Try to download the links - they are already sorted
            for link in episode.links():
                succeeded = download(link.direct(), series.configuration.path,
                                     str(episode))
                if succeeded:
                    logger.info("Downloaded episode {0}".format(episode))
                    break
                else:
                    logger.error("Failed to download episode {0}"
                                 .format(episode))


def cli():
    """
    This method is called when running pyseries from the command line
    """
    setup_logging()

    # Print version
    if sys.argv[1] in ['-v', '--version']:
        print('pyseries version {0}'.format(__version__))
        exit()

    # If a directory is given...
    if len(sys.argv) == 2:
        main(os.path.abspath(sys.argv[1]))
    else:
        # Use CWD instead...
        main(os.getcwd())

if __name__ == '__main__':
    cli()
