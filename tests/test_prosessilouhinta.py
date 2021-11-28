# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import datetime as dti
import pathlib

import pytest

import prosessilouhinta.prosessilouhinta as pm

BASIC_FIXTURES_PATH = pathlib.Path('tests', 'fixtures', 'basic')


def test_parse_empty_eventlog_csv():
    empty = BASIC_FIXTURES_PATH / 'empty.csv'
    assert pm.parse_eventlog_csv(empty) == {}


def test_parse_header_only_eventlog_csv():
    empty = BASIC_FIXTURES_PATH / 'header-only.csv'
    assert pm.parse_eventlog_csv(empty) == {}


def test_parse_single_data_line_eventlog_csv():
    empty = BASIC_FIXTURES_PATH / 'single-data-line.csv'
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.parse_eventlog_csv(empty) == eventlog


def test_parse_single_too_short_data_line_eventlog_csv():
    too_short = BASIC_FIXTURES_PATH / 'single-too-short-data-line.csv'
    message = r'not enough values to unpack \(expected 4, got 3\)'
    with pytest.raises(ValueError, match=message):
        _ = pm.parse_eventlog_csv(too_short)


def test_parse_single_ts_format_wrong_data_line_eventlog_csv():
    having_other_ts_format = BASIC_FIXTURES_PATH / 'single-ts-format-wrong-data-line.csv'
    message = r"time data '20211127T123456.654321Z' does not match format '%Y-%m-%d %H:%M:%S'"
    with pytest.raises(ValueError, match=message):
        _ = pm.parse_eventlog_csv(having_other_ts_format)


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


def test_control_flow_single_case_two_distinct_tasks():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:34:58', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u3', dti.datetime.strptime('2021-11-27 12:34:59', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.control_flow(eventlog) == {'t1': {'t2': 1}, 't2': {'t2': 2}}


def test_activity_counts_single_entry():
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.activity_counts(eventlog) == {'t1': 1}


def test_activity_counts_single_case_two_distinct_tasks():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:34:58', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u3', dti.datetime.strptime('2021-11-27 12:34:59', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.activity_counts(eventlog) == {'t1': 1, 't2': 3}


def test_user_activities_single_entry():
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.user_activities(eventlog) == {'u1': {'t1'}}


def test_user_activities__single_case_two_users():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
            ('t3', 'u1', dti.datetime.strptime('2021-11-27 12:34:58', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.user_activities(eventlog) == {'u1': {'t3', 't1'}, 'u2': {'t2'}}


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


def test_time_differences_single_case_two_tasks():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.time_differences(eventlog) == {'t1': {'t2': [dti.timedelta(seconds=1)]}}


def test_time_differences_single_case_two_distinct_tasks():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:34:58', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u3', dti.datetime.strptime('2021-11-27 12:34:59', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    expected_diffs = {
        't1': {'t2': [dti.timedelta(seconds=1)]},
        't2': {'t2': [dti.timedelta(seconds=1), dti.timedelta(seconds=1)]},
    }
    assert pm.time_differences(eventlog) == expected_diffs


def test_average_time_differences_single_case_two_users():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.average_time_differences(pm.time_differences(eventlog)) == {'t1': {'t2': dti.timedelta(seconds=1)}}
