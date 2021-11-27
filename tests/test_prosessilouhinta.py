# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import datetime as dti
import pathlib

import prosessilouhinta.prosessilouhinta as pm

FIXTURES_PATH = pathlib.Path('tests', 'fixtures')


def test_parse_empty_eventlog_csv():
    empty = FIXTURES_PATH / 'basic' / 'empty.csv'
    assert pm.parse_eventlog_csv(empty) == {}


def test_parse_header_only_eventlog_csv():
    empty = FIXTURES_PATH / 'basic' / 'header-only.csv'
    assert pm.parse_eventlog_csv(empty) == {}


def test_parse_single_data_line_eventlog_csv():
    empty = FIXTURES_PATH / 'basic' / 'single-data-line.csv'
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.parse_eventlog_csv(empty) == eventlog


def test_control_flow_single_entry():
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.control_flow(eventlog) == {}


def test_control_flow_single_case_two_tasks():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.control_flow(eventlog) == {'t1': {'t2': 1}}


def test_activity_counts_single_entry():
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.activity_counts(eventlog) == {'t1': 1}


def test_user_activities_single_entry():
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.user_activities(eventlog) == {'u1': set(['t1'])}


def test_work_distribution_single_entry():
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.work_distribution(eventlog) == {'u1': {'t1': 1}}


def test_working_together_single_entry():
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.working_together(eventlog) == {}


def test_working_together_single_case_two_users():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.working_together(eventlog) == {'u1': {'u2': 1}}


def test_time_differences_single_case_two_users():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.time_differences(eventlog) == {'t1': {'t2': [dti.timedelta(seconds=1)]}}
