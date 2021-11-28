# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import pathlib

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
    result = runner.invoke(app, ['unknown'])
    assert result.exit_code == 2


def test_cli_main(capsys):
    message = 'received wrong number of arguments'
    cli.main(['extract', 'no_file_there']) == 1
    captured = capsys.readouterr()
    assert message in captured.err


def test_cli_main_too_few_columns(capsys):
    """TODO(sthagen) passes as is will not when translation table is fixed (taken or removed)."""
    message = 'received wrong number of arguments'
    cli.main(['extract', BASIC_FIXTURES_PATH / 'single-too-short-data-line.csv']) == 1
    captured = capsys.readouterr()
    assert message in captured.err
