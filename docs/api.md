# API

Help on module prosessilouhinta.prosessilouhinta in prosessilouhinta:

## NAME

prosessilouhinta.prosessilouhinta - Process mining (Finnish prosessilouhinta) from eventlogs. API.


## DESCRIPTION

Typical programmatic API use is:

```python
import prosessilouhinta.prosessilouhinta as pm


def analyze(source: str) -> pm.Flow:
    """Extract control flow from eventlog source."""
    return pm.control_flow(pm.parse_eventlog_csv(source))
```

## FUNCTIONS

### Activity Counts:

```python
activity_counts(events: EventLog) -> dict[str, int]
    Calculate the activity counts A from eventlog.
```

### Average Time Differences

Uses `datetime.timedelta`s as type for the difference values

```python
average_time_differences(D: TimeDifference) -> AverageTimeDifference
    Average the time differences from D per case transitions.
```

### Average Time Differences

Uses `float`s as type for the difference values

```python
average_time_differences_as_float(AD: AverageTimeDifference) -> AverageTimeDifferenceFloats
    Convert the average time differences from D per case transitions to float.
```

### Control Flow:

```python
control_flow(events: EventLog) -> Flow
    Calculate the control flow from eventlog.
```

### CPA DIA

Support for the commandline API

```python
cpa_dia(argv: Optional[List[str]] = None) -> int
    Drive the CPA diagramming.
```

### Main

Support for the commandline API

```python
main(argv: Optional[List[str]] = None) -> int
    Drive the extraction.
```

### Eventlog Parser

This function accepts both a `pathlib.Path` as well as `sys.stdin` or any other iterator over strings.

```python
parse_eventlog_csv(source: Union[pathlib.Path, Iterator[str]]) -> Union[EventLog, Any]
    Parse the eventlog into a map, matching the translation headers to columns.
```

### Unified Reader

This is the implementation [`parse_eventlog_csv`] uses.

```python
reader(source: Union[pathlib.Path, Iterator[str]]) -> Iterator[str]
    Context wrapper / generator to read the lines.
```

### Time Differences

Uses `datetime.timedelta`s as type for the difference values

```python
time_differences(events: EventLog) -> TimeDifference
    Calculate time differences D from eventlog.
```

### Time Differences

Uses `float`s as type for the difference values

```python
time_differences_as_float(D: TimeDifference) -> TimeDifferenceFloats
    Convert the time differences from D per case transitions to float.
```

### User Activities:

```python
user_activities(events: EventLog) -> UserActivity
    Calculate the set of activities UA performed by each user from the eventlog.
```

### Verify Request

Support for the commandline API

```python
verify_request(argv: Optional[List[str]]) -> Tuple[int, str, List[str]]
    Fail with grace.
```

### Work Distribution

```python
work_distribution(events: EventLog) -> Flow
    Calculate the count of activities UAC performed by each user from the eventlog.
```

### Working Together

```python
working_together(events: EventLog) -> Flow
    Calculate the working together matrix W from eventlog.
```

## DATA

```python
    CSV_HEAD_TOKEN = '#'
    CSV_SEP = ','
    DEBUG = None
    DEBUG_VAR = 'PROSESSILOUHINTA_DEBUG'
    DISPATCH = {
        STDIN: sys.stdin,
        STDOUT: sys.stdout,
    }
    ENCODING = 'utf-8'
    ENCODING_ERRORS_POLICY = 'ignore'
    STDIN = 'STDIN'
    STDOUT = 'STDOUT'
```

## TYPES

```python
EventLog = dict[str, List[Tuple[str, str, datetime.datetime]]]
Activity = dict[str, int]
Flow = dict[str, dict[str, int]]
TimeDifference = dict[str, dict[str, List[datetime.timedelta]]]
TimeDifferenceFloats = dict[str, dict[str, List[float]]]
AverageTimeDifference = dict[str, dict[str, datetime.timedelta]]
AverageTimeDifferenceFloats = dict[str, dict[str, float]]
UserActivity = dict[str, list[str]]
```

## FILE

```console
    prosessilouhinta/prosessilouhinta.py
```
