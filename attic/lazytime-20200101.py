#!/usr/bin/env python3
import os, sys, argparse, re
from datetime import datetime, timedelta
from pathlib import Path

LAZYTIME_LOG_PATH = Path(
    os.getenv("LAZYTIME_LOG_PATH", os.path.expanduser("~/.config/lazytime/journal.log"))
)

WEEKDAYS: list[str] = ["Mon ", "Tue ", "Wed ", "Thu ", "Fri ", "*Sat", "*Sun"]

# TODO: Add an entry object

# TODO: The aggregator should aggregate items based on their continuity over time,
# so that instead of "moments" we end up having "session" (start and end moment)
#
# This is the data that should be used.

# -----------------------------------------------------------------------------
#
# AGGREGATOR
#
# -----------------------------------------------------------------------------


class Aggregator(object):
    """Opens the lazytime log and aggregates events by project and days."""

    def __init__(self):
        self.projects = {}
        self.days = {}

    def parse(self, path: Path = LAZYTIME_LOG_PATH):
        if path.exists():
            with open(path, "rt") as f:
                for _ in f.readlines():
                    self.feed(_)
        return self

    def feed(self, line: str):
        line = line.strip()
        if line.startswith("#"):
            return None
        fields = line.split("\t")
        if len(fields) < 2:
            return None
        date = self.parseDate(fields[0])
        project = fields[1]
        self.addEntry(project, date)

    def parseDate(self, date: str) -> datetime:
        ymd, hms = date.split()
        Y, M, D = ymd.split("-")
        h, m, s = hms.split(":")
        return datetime(*(int(_) for _ in (Y, M, D, h, m, s)))

    def addEntry(self, project, date):
        self.projects.setdefault(project, []).append(date)
        day = "{0:04d}-{1:02d}-{2:02d}".format(date.year, date.month, date.day)
        self.days.setdefault(day, []).append((project, date))

    def getEntries(self, start=None, end=None, projects=None):
        now = datetime.now()
        start = start or datetime(1979, 1, 1)
        end = end or now
        start = datetime(*start) if isinstance(start, tuple) else start
        end = datetime(*end) if isinstance(end, tuple) else end
        result = {}
        for day, entries in self.days.items():
            entries = [
                _
                for _ in entries
                if _[1] >= start
                and (not end or _[1] < end)
                and self.hasProject(_, projects)
            ]
            if len(entries) > 0:
                result[day] = entries
        return sorted(result.items(), key=lambda _: _[0])

    def hasProject(self, entry, projects=None):
        if not projects:
            return True
        else:
            return entry[0] in projects


# -----------------------------------------------------------------------------
#
# REPORT
#
# -----------------------------------------------------------------------------


class Report(object):
    """Generates common reports based on an aggregator."""

    # We assume a 45min lunch break on average
    LUNCH_BREAK = (
        11 * 60 + 45,
        12 * 60 + 45,
    )

    def __init__(self, aggregator):
        self.aggregator = aggregator

    def isWithinLunchBreak(self, date):
        t = date.hour * 60 + date.minute
        return t >= self.LUNCH_BREAK[0] and t <= self.LUNCH_BREAK[1]

    def secondsAsHours(self, seconds):
        h = int(seconds / 3600)
        m = int((seconds % 3600) / 60)
        return "{0:d}h{1:02d}".format(h, m)

    def getTimeSheet(
        self, week=0, output=sys.stdout, projects=None, start=None, end=None
    ):
        # We initialize an empty timedelta
        total = datetime(2018, 1, 1) - datetime(2018, 1, 1)
        output.write("DATE     \tDAY\tLOGGED\tTOTAL\tTASK\n")
        # We iterate on the entries per day
        for day, entries in self.aggregator.getEntries(start, end, projects):
            # We're going to group the entries by project
            last = None
            projects = {}
            for entry in entries:
                # A stop entry means it's the end of the day
                if entry[0] == "stop":
                    break
                # If it's not the first entry
                if last is not None:
                    delta = entry[1] - last[1]
                    duration = delta.total_seconds() / 60.0
                    # If the delta is more than 30min, and the last time entry
                    # is within the lunch break:
                    if duration > 30 and self.isWithinLunchBreak(last[-1]):
                        pass
                    else:
                        projects.setdefault(entry[0], last[1] - last[1])
                        projects[entry[0]] += delta
                last = entry
            # This is the formatting of the report
            if len(entries) > 1:
                result = sorted(
                    projects.items(), key=lambda _: _[1].total_seconds(), reverse=True
                )
                day_total = datetime(2018, 1, 1) - datetime(2018, 1, 1)
                day_str = str(day)
                day_blank = " " * len(day_str)
                weekday = WEEKDAYS[entry[1].weekday()]
                weekday_blank = " " * len(weekday)
                day_count = 0
                for i, v in enumerate(result):
                    project, delta = v
                    output.write(
                        "{0}\t{1}\t{2}\t\t{3}\n".format(
                            day_str if i == 0 else day_blank,
                            weekday if i == 0 else weekday_blank,
                            self.secondsAsHours(delta.total_seconds()),
                            project,
                        )
                    )
                    total += delta
                    day_total += delta
                    day_count += 1
                if day_count > 1:
                    output.write(
                        "\t\t\t\t{0}\tTOTAL/DAY\n".format(
                            self.secondsAsHours(day_total.total_seconds())
                        )
                    )
        output.write(
            "\t\t\t\t{0}\tTOTAL/PERIOD\n".format(
                self.secondsAsHours(total.total_seconds())
            )
        )


RE_DELTA = re.compile("(\d+)([wWdDmM])")
RE_DATE = re.compile("^(\d\d\d?\d?)([\-/](\d\d?)([-/](\d\d?))?)?")


def parse_time(text):
    text = text or ""
    now = datetime.now()
    now = datetime(year=now.year, month=now.month, day=now.day)
    m = RE_DELTA.match(text)
    if m:
        dur = m.group(2).lower()
        n = int(m.group(1))
        if dur == "w":
            d = timedelta(weeks=n)
        elif dur == "m":
            d = timedelta(months=n)
        elif dur == "y":
            d = timedelta(years=n)
        else:
            d = timedelta(days=n)
        return now - d
    m = RE_DATE.match(text)
    if m:
        y = int(m.group(1))
        d = int(m.group(5)) or 1
        m = int(m.group(3)) or 1
        return (y, m, d)
    elif text.lower() in ("w", "week"):
        return now - timedelta(days=now.weekday())
    else:
        return None


def command(args=None, name=os.path.basename(__file__).split(".", 1)[0]):
    if args is None:
        args = sys.argv[1:]
    if type(args) not in (type([]), type(())):
        args = [args]
    oparser = argparse.ArgumentParser(
        prog=name or os.path.basename(__file__.split(".")[0]),
        description="Produces reports based on tracked time entries",
    )
    # TODO: Rework command lines arguments, we want something that follows
    # common usage patterns.
    oparser.add_argument(
        "projects",
        metavar="projects",
        type=str,
        nargs="*",
        help="The name of the projects to track",
    )
    oparser.add_argument("--since", type=str, help="Since a specific date in time")
    oparser.add_argument("--before", type=str, help="Before a specific date in time")
    # We create the parse and register the options
    args = oparser.parse_args(args=args)
    out = sys.stdout
    entries = Aggregator().parse()
    report = Report(entries)
    since = parse_time(args.since)
    before = parse_time(args.before)
    report.getTimeSheet(projects=args.projects, start=since, end=before)


if __name__ == "__main__":
    command()

# EOF
