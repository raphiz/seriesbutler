# coding: utf-8
import click
import logging
from . import __version__ as version
from . import functions as fn
from .models import SeriesbutlerException
from .providers import Solarmovie, WatchTvSeries
from .datasources import TheTvDb


# Define, which link providers and datasources shall be used
link_providers = [Solarmovie(), WatchTvSeries()]
datasource = TheTvDb()
configuration = None


@click.group()
@click.version_option(version)
@click.option('-d', '--working-directory', type=click.Path(exists=True))
@click.option('-v', '--log-level', type=click.Choice(
              ['INFO', 'DEBUG', 'WARNING']), default='WARNING')
@click.pass_context
def cli(ctx, working_directory, log_level):
    """Download your favorite TV shows just by running one simple command"""
    fn._setup_logging(log_level)
    ctx.meta['working_directory'] = working_directory
    if not ctx.invoked_subcommand == 'init':
        global configuration
        try:
            configuration = fn.load_configuration(working_directory)
        except FileNotFoundError:
            raise click.ClickException('No configuration found! Please call'
                                       ' "seriesbutler init" first!')


@cli.command(name='list')
def list_series():
    """List all series managed by seriesbutler"""
    if len(configuration['series']) == 0:
        click.echo('No series registered yet! Call "seriesbutler add" to '
                   'register a new series.')
    for series in configuration['series']:
        click.echo(series['name'])


@cli.command()
def fetch():
    """Check for new episodes and download them"""

    # This is a ugly workaround to log on an info level...
    root_logger = logging.getLogger()
    if root_logger.getEffectiveLevel() > logging.INFO:
        root_logger.setLevel(logging.INFO)

    fn.fetch_all(configuration, link_providers, datasource)


@cli.command()
@click.pass_context
def init(ctx):
    """Initializes a directory to work with seriesbutler"""
    try:
        fn.init(ctx.meta['working_directory'])
        click.echo("Directory initialized to work with seriesbutler")
    except SeriesbutlerException as e:
        raise click.ClickException(str(e))


@cli.command()
def remove():
    """Remove a managed series"""
    series = configuration['series']

    if len(series) == 0:
        click.echo('No series to remove!')
        return

    click.echo("Which series shall be removed?")
    for idx, current in enumerate(series):
        click.echo("{0}. {1}".format(idx, current['name']))

    while 1:
        value = click.prompt('Enter the number of the series to remove',
                             type=int)
        if value >= 0 and value < len(series):
            break
        else:
            click.echo('OOps, that\'s not a valid option. Choose a value '
                       'between 0 and {0}!'.format(len(series)-1))

    name = series[value]['name']
    fn.remove_series(configuration, series[value])
    click.echo('Series {0} removed!'.format(name))


@cli.command()
def add():
    """Add a new series"""
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
    imdb = new_series[1]
    name = new_series[0]
    from_season, from_episode = 0, 0

    if click.confirm('Have you seen some episodes already?'):
        from_season = click.prompt(
            'The season of the last seen episode', type=int)
        from_episode = click.prompt(
            'The the last seen episode number', type=int)

    new_series = {'name': name, 'imdb': imdb, 'start_from':
                  {'season': from_season, 'episode': from_episode}}
    series = fn.add_series(configuration, new_series)

    click.echo("Added series {0}".format(series['name']))

if __name__ == '__main__':
    cli()
