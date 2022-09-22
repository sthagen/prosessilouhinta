import pathlib

from typer.testing import CliRunner

import prosessilouhinta
import prosessilouhinta.cli as cli
from prosessilouhinta.cli import app

BASIC_FIXTURES_PATH = pathlib.Path('test', 'fixtures', 'basic')

runner = CliRunner()


def test_app_version():
    result = runner.invoke(app, ['version'])
    assert result.exit_code == 0
    assert cli.APP_NAME in result.stdout
    assert prosessilouhinta.__version__ in result.stdout


def test_app_extract():
    result = runner.invoke(app, ['extract'])
    assert result.exit_code == 0


def test_app_unknown():
    result = runner.invoke(app, ['unknown', 'STDIN', 'does-not-exist'])
    assert result.exit_code == 2


def test_cli_main(capsys):
    message = 'received wrong number of arguments'
    assert cli.main(['extract', 'no_file_there']) == 2
    _, err = capsys.readouterr()
    assert message in err


def test_cli_main_unknown_command(capsys):
    message = 'received unknown command'
    assert cli.main(['unknown', 'STDIN', 'STDOUT', 'DRYRUN']) == 2
    _, err = capsys.readouterr()
    assert message in err


def test_cli_main_source_does_not_exist(capsys):
    message = 'source is no file'
    assert cli.main(['extract', 'source-does-not-exist', 'STDOUT', 'DRYRUN']) == 1
    _, err = capsys.readouterr()
    assert message in err


def test_cli_main_target_does_exist(capsys):
    message = 'target file exists'
    existing_file = str(BASIC_FIXTURES_PATH / 'existing-out-file.whatever')
    assert cli.main(['extract', existing_file, existing_file, 'DRYRUN']) == 1
    _, err = capsys.readouterr()
    assert message in err


def test_cli_main_verifier_passes(capsys):
    message = r'dryrun requested'
    existing_file = str(BASIC_FIXTURES_PATH / 'existing-out-file.whatever')
    assert cli.main(['extract', existing_file, 'target-does-not-exist', 'DRYRUN']) == 0
    _, err = capsys.readouterr()
    assert message in err


def test_cli_main_too_few_columns(capsys):
    message = 'received wrong number of arguments'
    assert cli.main(['extract', str(BASIC_FIXTURES_PATH / 'single-too-short-data-line.csv')]) == 2
    _, err = capsys.readouterr()
    assert message in err
