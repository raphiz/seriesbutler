# coding: utf-8
import click
import os
import shutil
from configobj import ConfigObj
from . import __version__ as version
import pyseries.functions as fn
from .providers import Solarmovie, WatchTvSeries
from .datasources import TheTvDb


# Define, which link providers and datasources shall be used
link_providers = [Solarmovie(), WatchTvSeries()]
datasource = TheTvDb()


@click.group()
@click.version_option(version)
def cli():
    """Download your favorite TV shows just by running one simple command"""
    fn.setup_logging()



@cli.command()
@click.argument('working_directory', required=False, type=click.Path(exists=True))
def fetch(working_directory):
    """Check for new episodes and download them"""
    working_directory = _normalize_working_directory(working_directory)
    fn.main(working_directory, link_providers, datasource)


@cli.command()
@click.argument('working_directory', type=click.Path(exists=True))
def remove(working_directory):
    """Remove an existing series from pyseries"""
    working_directory = _normalize_working_directory(working_directory)
    series = fn.load_series(working_directory, link_providers, datasource)

    if len(series) == 0:
        click.echo('No Episodes to remove!')
        return

    click.echo("Which Series shall be removed?")
    for idx, current in enumerate(series):
        click.echo("{0}. {1}".format(idx, current))

    while 1:
        value = click.prompt('Enter the number of the series to remove',
                             type=int)
        if value >= 0 and value < len(series):
            break
        else:
            click.echo('OOps, that\'s not a valid option. Choose a value '
                       'between 0 and {0}!'.format(len(series)-1))

    shutil.rmtree(series[value].configuration.path)
    click.echo('Series {0} removed!'.format(series[value]))


@cli.command()
@click.argument('working_directory', type=click.Path(exists=True))
def add(working_directory):
    """Add a new series from pyseries"""
    working_directory = _normalize_working_directory(working_directory)
    name = click.prompt('What\'s the title of the TV seris to add?')
    results = datasource.find_by_name(name)
    if len(results) == 0:
        click.echo('No results found!')
        return

    click.echo('Found {0} results'.format(len(results)))
    for idx, current in enumerate(results):
        click.echo("{0}. {1} ({2})".format(idx, current[0], current[1]))
    while 1:
        value = click.prompt('Enter the number of the series to add', type=int)
        if value >= 0 and value < len(results):
            break

    new_series = results[value]
    ini = ConfigObj(os.path.join(working_directory, new_series[0], 'info.ini'))
    ini['imdb'] = new_series[1]
    ini['name'] = new_series[0]

    if click.confirm('Have you seen some episodes already?'):
        ini['from_season'] = click.prompt(
            'The season of the last seen episode', type=int)
        ini['from_episode'] = click.prompt(
            'The the last seen episode number', type=int)

    os.mkdir(os.path.join(working_directory, new_series[0]))
    ini.write()

    click.echo("Added series {0}".format(new_series[0]))


def _normalize_working_directory(working_directory):
    if working_directory is None:
        return os.getcwd()
    else:
        return os.path.abspath(working_directory)

if __name__ == '__main__':
    cli()
