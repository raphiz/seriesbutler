from click.testing import CliRunner
from pyseries import cli
import pytest
import shutil
import json
import os
from vcr import VCR

vcr = VCR(cassette_library_dir=os.path.join(
    os.getcwd(), 'build/cassettes/cli/'))


@pytest.fixture
def fakedir(monkeypatch, tmpdir):
    # Add example config...
    shutil.copyfile('tests/data/examples/valid/pyseries.json',
                    tmpdir.join('pyseries.json').strpath)
    tmpdir.join('Brooklyn Nine-Nine').mkdir()

    # Change the working directory
    monkeypatch.chdir(tmpdir.strpath)

    return tmpdir


def test_list_series(fakedir):
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['list'])
    assert result.exit_code == 0

    assert result.output == 'Brooklyn Nine-Nine\n'

# TODO
def test_list_invalid_directory(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['list'])
    print(result)

# TODO
def test_init_empty_directory(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['init'])
    print(result)


@vcr.use_cassette()
def test_add_series_nothing_found(fakedir):
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['add'], input='lksjlakjsdl\n')
    print(result.exception)
    assert result.output == '''What's the title of the TV seris to add?: lksjlakjsdl
No results found!\n'''
    assert not fakedir.join('lksjlakjsdl').exists()


@vcr.use_cassette()
def test_add_series_happy_path(fakedir):
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['add'],
                           input='Breaking Bad\n0\ny\n4\n2\n')
    assert result.exit_code == 0
    assert result.output == '''What's the title of the TV seris to add?: Breaking Bad
Found 2 results
0. Breaking Bad (tt0903747)
1. Metastasis (tt3190448)
Enter the number of the series to add: 0
Have you seen some episodes already? [y/N]: y
The season of the last seen episode: 4
The the last seen episode number: 2
Added series Breaking Bad
'''
    config = json.loads(fakedir.join('pyseries.json').read())
    assert len(config['series']) == 2
    assert config['series'][1]['name'] == 'Breaking Bad'
    assert config['series'][1]['imdb'] == 'tt0903747'
    assert config['series'][1]['start_from']['season'] == 4
    assert config['series'][1]['start_from']['episode'] == 2

    assert fakedir.join('Breaking Bad').exists()


def test_remove_series_happy_path(fakedir):
    runner = CliRunner()
    result = runner.invoke(cli.cli, ['remove'],
                           input='-1\n0\n')
    assert result.output == '''Which series shall be removed?
0. Brooklyn Nine-Nine
Enter the number of the series to remove: -1
OOps, that\'s not a valid option. Choose a value between 0 and 0!
Enter the number of the series to remove: 0
Series Brooklyn Nine-Nine removed!
'''
    assert not fakedir.join('Brooklyn Nine-Nine').exists()
    config = json.loads(fakedir.join('pyseries.json').read())
    assert len(config['series']) == 0

    result = runner.invoke(cli.cli, ['remove'])
    assert result.output == 'No series to remove!\n'
