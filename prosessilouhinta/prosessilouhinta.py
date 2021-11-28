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
Activity = dict[str, int]
Flow = dict[str, dict[str, int]]
TimeDifference = dict[str, dict[str, List[dti.timedelta]]]
AverageTimeDifference = dict[str, dict[str, dti.timedelta]]
UserActivity = dict[str, set[str]]


def activity_counts(events: EventLog) -> Activity:
    """Calculate the activity counts A from eventlog."""
    A: Activity = {}
    for caseid in events:
        for i in range(0, len(events[caseid])):
            ai = events[caseid][i][0]
            if ai not in A:
                A[ai] = 0
            A[ai] += 1

    return A


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


def time_differences(events: EventLog) -> TimeDifference:
    """Calculate average time differences D from eventlog."""
    D: TimeDifference = {}
    for caseid in events:
        for i in range(0, len(events[caseid]) - 1):
            (ai, _, ti) = events[caseid][i]
            (aj, _, tj) = events[caseid][i + 1]
            if ai not in D:
                D[ai] = {}
            if aj not in D[ai]:
                D[ai][aj] = []
            D[ai][aj].append(tj - ti)

    return D


def average_time_differences(D: TimeDifference) -> AverageTimeDifference:
    """Average the time diferences from D per case transitions."""
    AD: AverageTimeDifference = {}
    for ai in sorted(D.keys()):
        AD[ai] = {}
        for aj in sorted(D[ai].keys()):
            sum_td = sum(D[ai][aj], dti.timedelta(0))
            count_td = len(D[ai][aj])
            avg_td = sum_td / count_td
            avg_td -= dti.timedelta(microseconds=avg_td.microseconds)
            AD[ai][aj] = avg_td

    return AD


def user_activities(events: EventLog) -> UserActivity:
    """Calculate the set of activities UA performed by each user from the eventlog."""
    UA: UserActivity = {}
    for caseid in events:
        for i in range(0, len(events[caseid])):
            ai = events[caseid][i][0]
            ui = events[caseid][i][1]
            if ui not in UA:
                UA[ui] = set()
            UA[ui].add(ai)

    return UA


def work_distribution(events: EventLog) -> Flow:
    """Calculate the count of activities UAC performed by each user from the eventlog."""
    UAC: Flow = {}
    for caseid in events:
        for i in range(0, len(events[caseid])):
            ai = events[caseid][i][0]
            ui = events[caseid][i][1]
            if ui not in UAC:
                UAC[ui] = {}
            if ai not in UAC[ui]:
                UAC[ui][ai] = 0
            UAC[ui][ai] += 1

    return UAC


def working_together(events: EventLog) -> Flow:
    """Calculate the working together matrix W from eventlog."""
    W: Flow = {}
    for caseid in events:
        S = set()
        for i in range(0, len(events[caseid])):
            ui = events[caseid][i][1]
            S.add(ui)
        L = sorted(list(S))
        for i in range(0, len(L) - 1):
            for j in range(i + 1, len(L)):
                ui = L[i]
                uj = L[j]
                if ui not in W:
                    W[ui] = {}
                if uj not in W[ui]:
                    W[ui][uj] = 0
                W[ui][uj] += 1

    return W


def parse_eventlog_csv(path: pathlib.Path) -> Union[EventLog, Any]:
    """Parse the eventlog into a map, matching the translation headers to columns."""
    evemtlog: EventLog = {}
    for line in reader(path):
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


def reader(path: pathlib.Path) -> Iterator[str]:
    """Context wrapper / generator to read the lines."""
    with open(path, 'rt', encoding=ENCODING) as handle:
        for line in handle:
            yield line


def verify_request(argv: Optional[List[str]]) -> Tuple[int, str, List[str]]:
    """Gail with grace."""
    if not argv or len(argv) != 4:
        return 2, 'received wrong number of arguments', ['']

    command, inp, out, dryrun = argv

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

    command, inp, out, dryrun = strings

    source = sys.stdin if not inp else reader(pathlib.Path(inp))
    if not source:
        return 2

    if dryrun:
        print('dryrun requested\n# ---', file=sys.stderr)
        print('* resources used:', file=sys.stderr)
        inp_disp = 'STDIN' if not inp else f'"{inp}"'
        out_disp = 'STDOUT' if not out else f'"{out}"'
        print(f'  - input from:       {inp_disp}', file=sys.stderr)
        print(f'  - output to:        {out_disp}', file=sys.stderr)

    return 0
