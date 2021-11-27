# -*- coding: utf-8 -*-
# pylint: disable=expression-not-assigned,line-too-long
"""Process mining (Finnish prosessilouhinta) from eventlogs. API."""
import datetime as dti
import json
import os
import pathlib
import sys
from json.decoder import JSONDecodeError
from typing import Any, Iterator, List, Optional, Tuple, Union

DEBUG_VAR = 'PROSESSILOUHINTA_DEBUG'
DEBUG = os.getenv(DEBUG_VAR)

ENCODING = 'utf-8'
ENCODING_ERRORS_POLICY = 'ignore'
CSV_HEAD_TOKEN = '#'
CSV_SEP = ','

STDIN, STDOUT = 'STDIN', 'STDOUT'
DISPATCH = {
    STDIN: sys.stdin,
    STDOUT: sys.stdout,
}

EventLog = dict[str, List[Tuple[str, str, dti.datetime]]]
Flow = dict[str, dict[str, int]]
Activity = dict[str, int]


def control_flow(events: EventLog) -> Flow:
    """Calculate the control flow from eventlog."""
    F: Flow = {}
    for caseid in events:
        for i in range(0, len(events[caseid]) - 1):
            ai = events[caseid][i][0]
            aj = events[caseid][i + 1][0]
            if ai not in F:
                F[ai] = {}
            if aj not in F[ai]:
                F[ai][aj] = 0
            F[ai][aj] += 1

    return F


def acitivty_counts(events: EventLog) -> Activity:
    """Calculate the activity counts A from eventlog."""
    A: Activity = {}
    for caseid in events:
        for i in range(0, len(events[caseid])):
            ai = events[caseid][i][0]
            if ai not in A:
                A[ai] = 0
            A[ai] += 1

    return A


def parse_eventlog_csv(path: pathlib.Path) -> Union[EventLog, Any]:
    """Parse the eventlog into a map, matching the translation headers to columns."""
    with open(path, encoding=ENCODING) as handle:
        evemtlog: EventLog = {}
        for line in handle:
            line = line.strip()
            if not line or line.startswith(CSV_HEAD_TOKEN):
                continue
            try:
                caseid, task, user, ts_text = line.split(CSV_SEP)[:4]
                timestamp = dti.datetime.strptime(ts_text, '%Y-%m-%d %H:%M:%S')
            except ValueError:  # Both statements may raise that wun
                print(line)
                raise
            if caseid not in evemtlog:
                evemtlog[caseid] = []
            event = (task, user, timestamp)
            evemtlog[caseid].append(event)
    return evemtlog


def load_translation_table(path: pathlib.Path) -> Union[dict[str, str], Any]:
    """Load the translation table into a tuple of unique non-idempotent pairs."""
    if not path:
        raise ValueError('translation table path not given')

    if not path.is_file():
        raise ValueError('translation table path must lead to a file')

    with open(path, 'r', encoding=ENCODING) as handle:
        try:
            table = json.load(handle)
        except JSONDecodeError:
            raise ValueError('translation table path must lead to a JSON file')

    if not table:
        raise ValueError('translation table is empty')

    return table


def reader(path: str) -> Iterator[str]:
    """Context wrapper / generator to read the lines."""
    with open(pathlib.Path(path), 'rt', encoding=ENCODING) as handle:
        for line in handle:
            yield line


def verify_request(argv: Optional[List[str]]) -> Tuple[int, str, List[str]]:
    """Gail with grace."""
    if not argv or len(argv) != 5:
        return 2, 'received wrong number of arguments', ['']

    command, inp, out, translation_table_path, dryrun = argv

    if command not in ('extract'):
        return 2, 'received unknown command', ['']

    if inp:
        if not pathlib.Path(str(inp)).is_file():
            return 1, 'source is no file', ['']

    if out:
        if pathlib.Path(str(out)).is_file():
            return 1, 'target file exists', ['']

    return 0, '', argv


def main(argv: Union[List[str], None] = None) -> int:
    """Drive the extraction."""
    error, message, strings = verify_request(argv)
    if error:
        print(message, file=sys.stderr)
        return error

    command, inp, out, translation_table_path, dryrun = strings

    table = load_translation_table(pathlib.Path(translation_table_path))
    if not table:
        return 1

    source = sys.stdin if not inp else reader(inp)
    if not source:
        return 2

    if dryrun:
        print('dryrun requested\n# ---', file=sys.stderr)
        print('* resources used:', file=sys.stderr)
        inp_disp = 'STDIN' if not inp else f'"{inp}"'
        out_disp = 'STDOUT' if not out else f'"{out}"'
        print(f'  - input from:       {inp_disp}', file=sys.stderr)
        print(f'  - output to:        {out_disp}', file=sys.stderr)
        print(f'  - translation from: "{translation_table_path}"', file=sys.stderr)

    return 0
