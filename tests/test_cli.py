# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
from typer.testing import CliRunner

import prosessilouhinta
import prosessilouhinta.cli as cli
from prosessilouhinta.cli import app

runner = CliRunner()


def test_app_version():
    result = runner.invoke(app, ['version'])
    assert result.exit_code == 0
    assert cli.APP_NAME in result.stdout
    assert prosessilouhinta.__version__ in result.stdout


def test_app_extract():
    result = runner.invoke(app, ['extract'])
    assert result.exit_code == 1


def test_cli_main(capsys):
    message = 'received wrong number of arguments'
    cli.main(['extract', 'no_file_there']) == 1
    captured = capsys.readouterr()
    assert message in captured.err
