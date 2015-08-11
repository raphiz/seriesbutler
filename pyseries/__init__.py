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


def setup_logging():
    """
        Setup logging configuration
    """
    logging.config.dictConfig(
        {'version': 1,
         'disable_existing_loggers': False,  # this fixes the problem
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
                 'level': 'INFO',
                 'handlers': ['console']
             },
             'requests': {
                 'level': 'WARNING',
                 'handlers': ['console']
             }
         }
         })


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
        logger.info('pyseries version {0}'.format(__version__))
        exit()

    # If a directory is given...
    if len(sys.argv) == 2:
        main(os.path.abspath(sys.argv[1]))
    else:
        # Use CWD instead...
        main(os.getcwd())

if __name__ == '__main__':
    cli()
