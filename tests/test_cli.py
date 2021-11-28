# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import pathlib

import pytest
from typer.testing import CliRunner

import prosessilouhinta
import prosessilouhinta.cli as cli
from prosessilouhinta.cli import app

BASIC_FIXTURES_PATH = pathlib.Path('tests', 'fixtures', 'basic')

runner = CliRunner()


def test_app_version():
    result = runner.invoke(app, ['version'])
    assert result.exit_code == 0
    assert cli.APP_NAME in result.stdout
    assert prosessilouhinta.__version__ in result.stdout


def test_app_extract():
    result = runner.invoke(app, ['extract'])
    assert result.exit_code == 1


def test_app_unknown():
    result = runner.invoke(app, ['unknown', '-t', 'does-not-exist'])
    assert result.exit_code == 2


def test_cli_main(capsys):
    message = 'received wrong number of arguments'
    cli.main(['extract', 'no_file_there']) == 1
    captured = capsys.readouterr()
    assert message in captured.err


def test_cli_main_unknown_command(capsys):
    message = 'received unknown command'
    cli.main(['unknown', 'STDIN', 'STDOUT', 'table-does-not-exist', 'DRYRUN']) == 2
    captured = capsys.readouterr()
    assert message in captured.err


def test_cli_main_source_does_not_exist(capsys):
    message = 'source is no file'
    cli.main(['extract', 'source-does-not-exist', 'STDOUT', 'table-does-not-exist', 'DRYRUN']) == 1
    captured = capsys.readouterr()
    assert message in captured.err


def test_cli_main_target_does_exist(capsys):
    message = 'target file exists'
    existing_file = str(BASIC_FIXTURES_PATH / 'existing-out-file.whatever')
    cli.main(['extract', existing_file, existing_file, 'table-does-not-exist', 'DRYRUN']) == 1
    captured = capsys.readouterr()
    assert message in captured.err


def test_cli_main_verifier_passes(capsys):
    message = r'translation table path must lead to a file'
    existing_file = str(BASIC_FIXTURES_PATH / 'existing-out-file.whatever')
    with pytest.raises(ValueError, match=message):
        _ = cli.main(['extract', existing_file, 'target-does-not-exist', 'table-does-not-exist', 'DRYRUN'])
        captured = capsys.readouterr()
        assert message in captured.err


def test_cli_main_too_few_columns(capsys):
    """TODO(sthagen) passes as is will not when translation table is fixed (taken or removed)."""
    message = 'received wrong number of arguments'
    cli.main(['extract', BASIC_FIXTURES_PATH / 'single-too-short-data-line.csv']) == 1
    captured = capsys.readouterr()
    assert message in captured.err
