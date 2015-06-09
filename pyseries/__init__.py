from bs4 import BeautifulSoup
import requests
import os
import copy
import logging.config
import logging
import json
from configobj import ConfigObj
import re
import youtube_dl
from contextlib import contextmanager
from .special_treatment import convert

__version__ = "0.0.2"
logger = logging.getLogger(__name__)

base = 'https://www.solarmovie.is'


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


@contextmanager
def pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)


def main():
    logger.info('Using pyseries v{0}'.format(__version__))
    download(os.getcwd())


def is_valid_config(path):
    #  TODO: this could be extended...
    config = ConfigObj(path)
    if config.get('imdb') is None:
        return False
    if config.get('imdb')[:2] != 'tt':
        logger.warn(
            'Please add the tt prefix from the imdb link in {0}!'.format(path)
        )
        return False
    return True


def fetch_url(imdb_id):
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }

    r = requests.get(
        '{0}/suggest-movie/?tv=all&term={1}'.format(base, imdb_id[2:]),
        headers=headers
    )

    if r.status_code != 200:
        logger.error("Status code {0} ({1})!".format(r.status_code, url))
        return None

    result = r.json()
    if len(result) != 1:
        logger.error(
            "Recieved an unexpected amount of results: {0}"
            .format(len(result))
        )
        return None
    return base + result[0]['url']


def scrape_episodes(url):
    r = requests.get(url)
    if r.status_code != 200:
        logger.error("Status code {0} ({1})!".format(r.status_code, url))
        return None

    soup = BeautifulSoup(r.text)
    box = soup.select('.seasonEpisodeListBox > div')[0]
    seasons = {}
    for value in range(0, len(box.contents)):
        element = box.contents[value]
        if element.name is None:
            continue
        if element.name == 'h4':
            name = element.find_all('a')[1].string.strip()
            episodes = {}
            next_box = box.contents[value+2]
            for episode_box in next_box.select('.js-episode'):
                episode_no = int(episode_box.a.string[8:])
                episodes[episode_no] = {
                    'link': base + episode_box.a['href'],
                    'date': episode_box.em.string,
                }
            season_no = int(name[7:])
            seasons[season_no] = {
                'season': name,
                'episodes': episodes
                }
    return seasons


def remove_unwanted(details, config, path, ignore_fs=False):
    from_season = config.get('from_season')
    if from_season is None:
        from_season = 1
    from_season = int(from_season)
    from_episode = config.get('from_episode')
    if from_episode is None:
        from_episode = 1
    from_episode = int(from_episode)

    if ignore_fs is not True:
        for filename in os.listdir(path):
            match = re.fullmatch('s([0-9]*)e([0-9]*)\..*', filename)
            if match:
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

    for (season_no, season) in copy.copy(details).items():
        if season_no < from_season:
            logger.info(
                "Skipping season {0} for series {1}".format(
                    season_no,
                    config.get('imdb')
                )
            )
            del details[season_no]
            continue
        for (episode_no, episode) in copy.copy(season['episodes']).items():
            if episode_no < from_episode and \
               from_season == season_no:
                logger.info(
                    "Skipping episode s{0}e{1} for series {2}".format(
                        season_no,
                        episode_no,
                        config.get('imdb')
                    )
                )
                del season['episodes'][episode_no]
                continue

    return details


def download_episodes(details, target_dir):
    for (season_no, season) in details.items():
        for (episode_no, episode) in season['episodes'].items():
            download_link(
                episode['link'],
                target_dir,
                's{0}e{1}'.format(season_no, episode_no)
            )


def download_link(url, target_dir, name):
    r = requests.get(url)
    if r.status_code != 200:
        logger.error("Status code {0} ({1})!".format(r.status_code, url))
        return None

    soup = BeautifulSoup(r.text)
    with pushd(target_dir):
        for elm in soup.select('.dataTable tbody tr'):
            # TODO: skip unwanted hosters!

            if not elm.has_attr('id'):
                continue
            direct = convert(unwrap(
                'http://solarmovie.is/link/play/{0}/'.format(elm['id'][5:])
            ))
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': name + '.%(ext)s'
                }
                logger.info("Downloading from ... {0}".format(direct))

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([direct])
                    return True
            except Exception as e:
                if 'embed' in direct:
                    logger.warn(
                        'Link {0} might be embedded - special treatment?'
                        .format(direct)
                    )
                else:
                    logger.info(
                        'Failed to download from link {0}'.format(direct)
                    )
    logger.error('No links found for {0}'.format(name))


def unwrap(url):
    r = requests.get(url)
    if r.status_code != 200:
        logger.error("Status code {0} ({1})!".format(r.status_code, url))
        return None
    soup = BeautifulSoup(r.text)
    return soup.select('iframe')[0]['src']


def download(working_dir):
    logger.info('Working directory is {0}'.format(os.getcwd()))

    # For each file in the root directory
    for value in os.listdir(working_dir):
        #  If the current file is a directory and contains a file called
        # info.ini
        path = os.path.join(working_dir, value)
        config_file = os.path.join(path, 'info.ini')
        if os.path.isdir(path) and \
           os.path.isfile(config_file) and \
           is_valid_config(config_file):
            logger.info(
                'Investigating into folder "{0}"...'.format(value)
            )

            config = ConfigObj(config_file)
            url = fetch_url(config.get('imdb'))
            if url is None:
                continue

            details = scrape_episodes(url)
            details = remove_unwanted(details, config, path)

            download_episodes(details, path)
        else:
            logger.info(
                'Skipping folder "{0}" - does not contain a info.ini'
                .format(value)
            )

setup_logging()

if __name__ == '__main__':
    main()
