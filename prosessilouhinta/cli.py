#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""Commandline API gateway for prosessilouhnita."""
import sys
from typing import Any, List, Union

import typer

import prosessilouhinta
import prosessilouhinta.prosessilouhinta as pm

APP_NAME = 'Process mining (Finnish prosessilouhinta) from eventlogs.'
APP_ALIAS = 'prosessilouhnita'
app = typer.Typer(
    add_completion=False,
    context_settings={'help_option_names': ['-h', '--help']},
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def callback(
    version: bool = typer.Option(
        False,
        '-V',
        '--version',
        help='Display the prosessilouhinta version and exit',
        is_eager=True,
    )
) -> None:
    """
    Process mining (Finnish prosessilouhinta) from eventlogs.
    """
    if version:
        typer.echo(f'{APP_NAME} version {prosessilouhinta.__version__}')
        raise typer.Exit()


@app.command('extract')
def extract(
    source: str = typer.Argument(pm.STDIN),
    target: str = typer.Argument(pm.STDOUT),
    inp: str = typer.Option(
        '',
        '-i',
        '--input',
        help='Path to input eventlog file (default is reading from standard in)',
        metavar='<sourcepath>',
    ),
    out: str = typer.Option(
        '',
        '-o',
        '--output',
        help='Path to non-existing output report file (default is writing to standard out)',
        metavar='<targetpath>',
    ),
    dry: bool = typer.Option(
        False,
        '-n',
        '--dryrun',
        help='Flag to execute without writing the extraction but a summary instead (default is False)',
        metavar='bool',
    ),
) -> int:
    """
    Translate from a language to a 'langauge'.
    """
    command = 'extract'
    incoming = inp if inp else (source if source != pm.STDIN else '')
    outgoing = out if out else (target if target != pm.STDOUT else '')
    dryrun = 'DRYRUN' if dry else ''
    action = [command, incoming, outgoing, dryrun]
    return sys.exit(pm.main(action))


@app.command('version')
def app_version() -> None:
    """
    Display the afasi version and exit
    """
    callback(True)


# pylint: disable=expression-not-assigned
# @app.command()
def main(argv: Union[List[str], None] = None) -> Union[int, Any]:
    """Delegate processing to functional module."""
    argv = sys.argv[1:] if argv is None else argv
    return pm.main(argv)
