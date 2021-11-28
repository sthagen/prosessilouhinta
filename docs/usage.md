# Example Usage

For use from python programs cf. [API](api.md)

On the command line given an eventlog like:

```console
$ cat tests/fixtures/basic/small-eventlog.csv
#case_id,task,user,ts_text
c1,t1,u1,2021-11-27 12:34:56
c1,t2,u2,2021-11-27 12:34:57
c1,t3,u3,2021-11-27 12:34:58
c2,t1,u1,2021-11-27 12:34:57
c2,t2,u1,2021-11-27 12:34:58
c2,t3,u2,2021-11-27 12:34:59
c3,t1,u1,2021-11-27 12:34:56
c3,t2,u2,2021-11-27 12:34:57
c3,t3,u3,2021-11-27 12:34:58
c4,t1,u1,2021-11-27 12:34:51
c5,t1,u1,2021-11-27 12:31:52
c5,t2,u2,2021-11-27 12:31:53
c5,t3,u3,2021-11-27 12:31:54
c5,t4,u4,2021-11-27 12:31:55
c6,t1,u1,2021-11-27 12:34:52
c6,t2,u2,2021-11-27 12:34:53
c7,t1,u1,2021-11-27 12:34:54
c8,t1,u1,2021-11-27 12:34:55
c9,t1,u1,2021-11-27 12:34:56
c10,t1,u1,2021-11-27 12:34:57
c10,t2,u3,2021-11-27 13:34:57
```

Asking for a dryrun:

```console
$ prosessilouhinta extract --dryrun < tests/fixtures/basic/small-eventlog.csv
dryrun requested
# ---
* resources used:
  - input from:       STDIN
  - output to:        STDOUT
```

Calling the app (and piping the out put into jq) gives:

```console
$ prosessilouhinta extract  < tests/fixtures/basic/small-eventlog.csv | jq . -C
{
  "activity_counts": {
    "t1": 10,
    "t2": 6,
    "t3": 4,
    "t4": 1
  },
  "average_time_differences": {
    "t1": {
      "t2": 600
    },
    "t2": {
      "t3": 1
    },
    "t3": {
      "t4": 1
    }
  },
  "control_flow": {
    "t1": {
      "t2": 6
    },
    "t2": {
      "t3": 4
    },
    "t3": {
      "t4": 1
    }
  },
  "time_differences": {
    "t1": {
      "t2": [
        1,
        1,
        1,
        1,
        1,
        3600
      ]
    },
    "t2": {
      "t3": [
        1,
        1,
        1,
        1
      ]
    },
    "t3": {
      "t4": [
        1
      ]
    }
  },
  "user_activities": {
    "u1": [
      "t1",
      "t2"
    ],
    "u2": [
      "t2",
      "t3"
    ],
    "u3": [
      "t2",
      "t3"
    ],
    "u4": [
      "t4"
    ]
  },
  "work_distribution": {
    "u1": {
      "t1": 10,
      "t2": 1
    },
    "u2": {
      "t2": 4,
      "t3": 1
    },
    "u3": {
      "t3": 3,
      "t2": 1
    },
    "u4": {
      "t4": 1
    }
  },
  "working_together": {
    "u1": {
      "u2": 5,
      "u3": 4,
      "u4": 1
    },
    "u2": {
      "u3": 3,
      "u4": 1
    },
    "u3": {
      "u4": 1
    }
  }
}
```

Currently not much more is implemented.

Asking for help:

```console
$ prosessilouhinta
Usage: prosessilouhinta [OPTIONS] COMMAND [ARGS]...

  Process mining (Finnish prosessilouhinta) from eventlogs.

Options:
  -V, --version  Display the prosessilouhinta version and exit
  -h, --help     Show this message and exit.

Commands:
  extract  Translate from a language to a 'langauge'.
  version  Display the afasi version and exit
```

Finding the version:

```console
prosessilouhinta version
$ Process mining (Finnish prosessilouhinta) from eventlogs. version 2021.11.27
```
