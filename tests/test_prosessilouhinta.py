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
    single = BASIC_FIXTURES_PATH / 'single-data-line.csv'
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.parse_eventlog_csv(single) == eventlog


def test_parse_two_cases_two_data_lines_eventlog_csv():
    two_cases = BASIC_FIXTURES_PATH / 'two-cases-two-data-lines.csv'
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
        ],
        'c2': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
        ],
    }
    assert pm.parse_eventlog_csv(two_cases) == eventlog


def test_parse_wun_case_two_data_lines_eventlog_csv():
    two_cases = BASIC_FIXTURES_PATH / 'wun-case-two-data-lines.csv'
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
        ],
    }
    assert pm.parse_eventlog_csv(two_cases) == eventlog


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
    assert pm.user_activities(eventlog) == {'u1': ['t1']}


def test_user_activities_single_case_two_users():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
            ('t3', 'u1', dti.datetime.strptime('2021-11-27 12:34:58', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.user_activities(eventlog) == {'u1': ['t1', 't3'], 'u2': ['t2']}


def test_work_distribution_single_entry():
    eventlog = {'c1': [('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S'))]}
    assert pm.work_distribution(eventlog) == {'u1': {'t1': 1}}


def test_work_distribution_single_case_two_distinct_tasks_two_users():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:58', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.work_distribution(eventlog) == {'u1': {'t1': 2}, 'u2': {'t2': 1}}


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


def test_working_together_single_case_three_users():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t1', 'u2', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
            ('t1', 'u3', dti.datetime.strptime('2021-11-27 12:34:58', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:59', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:35:00', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u3', dti.datetime.strptime('2021-11-27 12:36:01', '%Y-%m-%d %H:%M:%S')),
        ]
    }
    assert pm.working_together(eventlog) == {'u1': {'u2': 1, 'u3': 1}, 'u2': {'u3': 1}}


def test_working_together_two_cases_three_users():
    eventlog = {
        'c1': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t1', 'u2', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
            ('t1', 'u3', dti.datetime.strptime('2021-11-27 12:34:58', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:59', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:35:00', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u3', dti.datetime.strptime('2021-11-27 12:36:01', '%Y-%m-%d %H:%M:%S')),
        ],
        'c2': [
            ('t1', 'u1', dti.datetime.strptime('2021-11-27 12:34:56', '%Y-%m-%d %H:%M:%S')),
            ('t1', 'u2', dti.datetime.strptime('2021-11-27 12:34:57', '%Y-%m-%d %H:%M:%S')),
            ('t1', 'u3', dti.datetime.strptime('2021-11-27 12:34:58', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u1', dti.datetime.strptime('2021-11-27 12:34:59', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u2', dti.datetime.strptime('2021-11-27 12:35:00', '%Y-%m-%d %H:%M:%S')),
            ('t2', 'u3', dti.datetime.strptime('2021-11-27 12:36:01', '%Y-%m-%d %H:%M:%S')),
        ],
    }
    assert pm.working_together(eventlog) == {'u1': {'u2': 2, 'u3': 2}, 'u2': {'u3': 2}}


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


def test_verify_request():
    message = 'received wrong number of arguments'
    request = ['extract', 'no_file_there']
    assert pm.verify_request(request) == (2, message, [''])


def test_verify_request_unknown_command():
    message = 'received unknown command'
    request = ['unknown', 'STDIN', 'STDOUT', 'DRYRUN']
    assert pm.verify_request(request) == (2, message, [''])


def test_verify_request_source_does_not_exist():
    message = 'source is no file'
    request = ['extract', 'source-does-not-exist', 'STDOUT', 'DRYRUN']
    assert pm.verify_request(request) == (1, message, [''])


def test_verify_request_target_does_exist():
    message = 'target file exists'
    existing_file = str(BASIC_FIXTURES_PATH / 'existing-out-file.whatever')
    request = ['extract', existing_file, existing_file, 'DRYRUN']
    assert pm.verify_request(request) == (1, message, [''])


def test_verify_request_verifier_passes():
    existing_file = str(BASIC_FIXTURES_PATH / 'existing-out-file.whatever')
    request = ['extract', existing_file, 'target-does-not-exist', 'DRYRUN']
    assert pm.verify_request(request) == (0, '', request)
