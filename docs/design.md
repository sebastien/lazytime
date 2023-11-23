
# Overall

- A simple database model that tracks actions performed on things 
- A vocabulary of actions to track time spent
- A supporting shell tool that infers time spent based on activity

# Model

## Raw journal

Data model:

- `entry`: incremental id, based on Epoch time.
- `timestamp`: ISO dateformat with timezone
- `subject`: the subject (task, project), `/`-separated
- `action`: the action performed on the subject
- `value`: the optional value associated with the action
- `data`: additional context on the event (typically tags)

Features:

- Journal can be easily merged by using the `entry` id
- Journal can be archived using `YYYY-DD-MM` and doing a cut-off by date

# Reports data:

- Read from the raw journal from a given entry id

## Actions

- `Start`: starts tracking time on the given subject
- `End`: stops tracking time on the given subject
- `Log(duration:s)`: logs a duration of time tracked

# Shell tool

- Works on prompt change
- Infers the subject of an action based on a `.lazytime` file or if we're
  within a git repository.
- Detects breaks after some timeout with no interaction
- Can take into account the version control history and changes on the files
- Generates actions in the raw journal corresponding


# Reports

Some of the principles:

- Items are numbered so that they can be referenced
- Display is like tabular format

Filters:

- Time range: since, between
- Include/exclude: project(s), meta

## Subjects

```
01 projects                                             3000h (1Y2M/3Y)
02    personal                                           399h (2W/1Y)
03        lazytime                                        10h (2W/2Y)
04    work
05        platform
```

## Journal

Gives the last 100 entries of the journal, grouping them by weekday, week
and month.

```
=== Week #20 (2023-10):                                    23h/20h
 …
=== Last week:                                             23h/20h
 …
=== This week:                                             23h/20h
--- Monday:                                                4h/10h
008 -  project/personal/notes                              10min (0.2%)
009 -  project/personal/project                            10min (0.2%)
010 -  <break>                                             [120min]
 - …
```

# CLI

- `lazytime-autorecorder` as a prompt-helper to for shells
- `lazytime start SUBJECT DATA…`
- `lazytime running`, to show the current running task
- `lazytime stop`, to stop the current running task
- `lazytime log SUBJECT DURATION DATA…`

