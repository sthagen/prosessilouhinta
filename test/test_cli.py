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


def test_cli_main():
    message = 'source is no file'
    result = runner.invoke(app, ['extract', 'no_file_there'])
    assert result.exit_code == 1
    assert message in result.stdout


def test_cli_main_unknown_command():
    message = 'No such command'
    result = runner.invoke(app, ['unknown', 'STDIN', 'STDOUT', 'DRYRUN'])
    assert result.exit_code == 2
    assert message in result.stdout


def test_cli_main_source_does_not_exist():
    message = 'source is no file'
    result = runner.invoke(app, ['extract', 'source-does-not-exist', 'STDOUT', '-n'])
    assert result.exit_code == 1
    assert message in result.stdout


def test_cli_main_target_does_exist():
    message = 'target file exists'
    existing_file = str(BASIC_FIXTURES_PATH / 'existing-out-file.whatever')
    result = runner.invoke(app, ['extract', existing_file, existing_file, '--dryrun'])
    assert result.exit_code == 1
    assert message in result.stdout


def test_cli_main_verifier_passes():
    message = r'dryrun requested'
    existing_file = str(BASIC_FIXTURES_PATH / 'existing-out-file.whatever')
    result = runner.invoke(app, ['extract', existing_file, '-o', 'target-does-not-exist', '-n'])
    assert result.exit_code == 0
    assert message in result.stdout


def test_cli_main_too_few_columns():
    message = 'c1,t1,2021-11-27 12:34:56'
    # error = 'not enough values to unpack (expected 4, got 3)'
    result = runner.invoke(app, ['extract', str(BASIC_FIXTURES_PATH / 'single-too-short-data-line.csv')])
    assert result.exit_code == 1
    assert message in result.stdout
