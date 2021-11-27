# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import pathlib

import prosessilouhinta.prosessilouhinta as pm

FIXTURES_PATH = pathlib.Path('tests', 'fixtures')


def test_parse_empty_eventlog_csv():
    empty = FIXTURES_PATH / 'basic' / 'empty.csv'
    assert pm.parse_eventlog_csv(empty) == {}


def test_parse_header_only_eventlog_csv():
    empty = FIXTURES_PATH / 'basic' / 'header-only.csv'
    assert pm.parse_eventlog_csv(empty) == {}
