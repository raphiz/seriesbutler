from .functions import download, remove_ignored, load_series
from .providers import Solarmovie
from .datasources import TheTvDb
import logging

logger = logging.getLogger(__name__)


def main(working_directory):
    # Define, which link providers and datasources shall be used
    link_providers = [Solarmovie()]
    datasource = TheTvDb()

    for series in load_series(working_directory, link_providers, datasource):

        episodes = series.episodes()

        # Remove the episodes that are ignored - or
        episodes = remove_ignored(series, episodes)

        for episode in episodes:
            # Try to download the links - they are already sorted
            for link in episode.links():
                succeeded = download(link.direct(), working_directory,
                                     str(episode))
                if succeeded:
                    logger.info("Downloaded episode {0}".format(episode))
                    break

            if not succeeded:
                logger.error("Failed to download episode {0}".format(episode))

if __name__ == '__main__':
    main()
