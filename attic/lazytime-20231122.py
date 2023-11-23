#!/usr/bin/env python

__doc__ = """
Lazytime is a command-line tool and a Python API to manage a
project-based time tracking tool where time entries are inferred from registered
events.

Lazytime makes it possible to *implicitly log hours* by analyzing the stream of
events that is recorded."""

DATABASE_PATH = "~/.config/lazytime/journal.db"

# === IMPORTS =================================================================

import os, re, sys, json, logging, collections
import dateutil.parser
from datetime import datetime
from typing import Optional, Any

try:
    import sqlite3
except ImportError as e:
    logging.error("Module 'sqlite3' is required, but does not seem available.")
# SEE: https://click.palletsprojects.com/en/7.x/
try:
    import click
except ImportError as e:
    logging.error(
        "Module 'click' is required, but does not seem available. Try `pip3 install --user --upgrade click`"
    )

# === TYPES ===================================================================

Arguments = Any
Project = collections.namedtuple("Project", ("id", "name"))
Event = collections.namedtuple(
    "Event", ("id", "project", "timestamp", "command", "arguments")
)

# === INTERNAL GLOBALS ========================================================

RE_NOT_ID = re.compile("[^A-Za-z0-9]")
RE_SPACES = re.compile("\s*")

# -----------------------------------------------------------------------------
#
# CONNECTOR
#
# -----------------------------------------------------------------------------


class Connector:
    def getProjectID(self, project: str):
        """Returns a normalized project ID from the given project."""
        return RE_NOT_ID.sub("-", RE_SPACES.sub(" ", project.lower()))

    def addProject(self, project: str, name: Optional[str] = None):
        """Adds a new project."""
        return self.ensureProject(project, name)

    def ensureProject(self, project: str, name: Optional[str] = None):
        raise NotImplementedError

    def iterProjects(self):
        raise NotImplementedError

    def listProjects(self):
        return list(self.iterProjects())

    # =========================================================================
    # EVENTS
    # =========================================================================

    def addEvent(self, project: str, command: str, arguments: Optional[Arguments]):
        raise NotImplementedError

    def iterEvents(
        self,
        project: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ):
        raise NotImplementedError

    def listEvents(
        self,
        project: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ):
        return list(self.iterEvents(project=project, after=after, before=before))

    # =========================================================================
    # SPECIAL
    # =========================================================================

    def __enter__(self):
        """Ensures that there is a connection & cursor open when entereing
        the connectors' context."""
        # Makes sure there is a cursor
        cursor = self.cursor
        return self

    def __exit__(self, type, value, traceback):
        """Closes and commits any change."""
        self.close()


# -----------------------------------------------------------------------------
#
# SQL CONNECTOR
#
# -----------------------------------------------------------------------------


class SQLConnector(Connector):
    """An SQLite connector to the Lazytime data model."""

    SQL_MODEL = (
        """
	CREATE TABLE  IF NOT EXISTS projects (
		id        TEXT PRIMARY KEY NULL,
		name      TEXT NOT NULL
	);""",
        """CREATE TABLE IF NOT EXISTS events (
		id           INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		project      TEXT NOT NULL,
		timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP,
		command      TEXT NOT NULL,
		arguments    JSON,
		FOREIGN KEY (project) REFERENCES projects (id)
			ON DELETE CASCADE
			ON UPDATE CASCADE
	);""",
    )

    def __init__(self, path: Optional[str] = None):
        self.path: str = path or DATABASE_PATH
        self._connection: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None

    @property
    def cursor(self) -> sqlite3.Cursor:
        if not self._cursor:
            self.open()
        assert self._cursor
        return self._cursor

    # =========================================================================
    # DB
    # =========================================================================

    def open(self):
        """Makes sure that there is an open connection and cursor to
        the SQLite databse."""
        if self._connection:
            return self
        else:
            # Ensures that the path exists
            path = os.path.expanduser(self.path)
            parent_path = os.path.dirname(path)
            if parent_path and not os.path.exists(parent_path):
                os.makedirs(parent_path)
            # And opens/inits the SQLite database
            should_init = not os.path.exists(path)
            self._connection = sqlite3.connect(path)
            self._cursor = self._connection.cursor()
            if should_init:
                for _ in self.SQL_MODEL:
                    self._cursor.execute(_)
                self._connection.commit()
            return self

    def close(self):
        """Commits any uncommited changes and closes both the cursor and
        the connection."""
        self._connection.commit()
        self._cursor.close()
        self._connection.close()

    # =========================================================================
    # PROJECTS
    # =========================================================================

    def ensureProject(self, project: str, name: Optional[str] = None):
        if name is None:
            name = project
            project = self.getProjectID(name)
        # We normalize the project ID in all cases
        project = self.getProjectID(project)
        self.cursor.execute(
            "INSERT OR IGNORE INTO projects(id,name) VALUES (?,?)", (project, name)
        )
        return project

    def iterProjects(self):
        for row in self.cursor.execute("SELECT * FROM projects"):
            yield Project(*row)

    # =========================================================================
    # EVENTS
    # =========================================================================

    def addEvent(self, project: str, command: str, arguments: Optional[Arguments]):
        project_id = self.ensureProject(project)
        return self.cursor.execute(
            "INSERT INTO events (project,command,arguments)" "VALUES (?, ?, ?)",
            (project_id, command, json.dumps(arguments)),
        )

    def iterEvents(
        self,
        project: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
    ):
        query = "SELECT * FROM events"
        for id, project, timestamp, command, arguments in self.cursor.execute(query):
            yield Event(id, project, timestamp, command, json.loads(arguments))

    # =========================================================================
    # SPECIAL
    # =========================================================================

    def __enter__(self):
        """Ensures that there is a connection & cursor open when entereing
        the connectors' context."""
        # Makes sure there is a cursor
        cursor = self.cursor
        return self

    def __exit__(self, type, value, traceback):
        """Closes and commits any change."""
        self.close()


# -----------------------------------------------------------------------------
#
# REPORT
#
# -----------------------------------------------------------------------------


class Report:
    """The abstract foundation for reporting data. A report is run on a
    a series of events."""

    def process(self, events):
        raise NotImplementedError

    def header(self, *args):
        return ("H", args)

    def row(self, *args):
        return ("R", args)

    def sep(self, *args):
        return ("S", args)

    def newline(self):
        return ("N",)

    def summary(self, label, value):
        return ("S", label, value)


# -----------------------------------------------------------------------------
#
# RAW EVENT LIST
#
# -----------------------------------------------------------------------------


class RawEventReport(Report):
    """Outputs the list of events, as they appear in the event stream, without any
    kind of aggregation."""

    def process(self, events):
        yield self.header("Project", "Timestamp", "Op", "Args")
        for e in events:
            yield self.row(e.project, e.timestamp, e.command, json.dumps(e.arguments))


# -----------------------------------------------------------------------------
#
# FORMATTER
#
# -----------------------------------------------------------------------------


class Formatter:
    """Formats the output generated by a a report, interpreting the directives
    as formatted text."""

    def __init__(self):
        self.out = sys.stdout
        self.previousRow = None

    def format(self, iterator):
        for op in iterator:
            if op[0] == "H":
                self.line("\t".join(_.upper() for _ in op[1]))
            elif op[0] == "R":
                self.line("\t".join(self._reformatRow(op[1])))
            elif op[0] == "S":
                self.line("---")
            elif op[0] == "N":
                self.line("")
            else:
                raise ValueError(f"Unsupported formatter operation: {op}")
        return self

    def line(self, text: str):
        self.out.write(text)
        self.out.write("\n")

    def _reformatRow(self, row):
        """Keeps track of the previous row, and only output something
        if it has a differnet value."""
        # FEATURE: When previous row has same value, display nothing.
        if not self.previousRow:
            self.previousRow = row
            yield from (_ for _ in row)
        else:
            for i, v in enumerate(row):
                n = len(self.previousRow)
                if i < n and row[i] == self.previousRow[i]:
                    yield "…"
                else:
                    yield v
            self.previousRow = row


# -----------------------------------------------------------------------------
#
# COMMAND
#
# -----------------------------------------------------------------------------


class Command:
    """Tools and functions implementing the command line interface."""

    # These are going to be mutated by the functions decoatred with the
    # click functions.

    INTERFACE = None

    @click.group()
    @click.option("--db", default=DATABASE_PATH, help="Path to database file")
    @click.pass_context
    def Run(ctx, db):
        options = {"db": db}
        # NOTE: We'll use the `pass_obj` later to get these options back
        # as a named object.
        ctx.obj = collections.namedtuple("Options", options.keys())(*options.values())

    @Run.command(help="Lists projects that have entries")
    @click.pass_obj
    def Projects(options):
        with SQLConnector(options.db) as c:
            print(c.listProjects())

    @Run.command(help="Lists projects that have entries")
    @click.pass_obj
    def Events(options):
        with SQLConnector(options.db) as c:
            Formatter().format(RawEventReport().process(c.iterEvents()))

    @Run.command(help="Lists events with different grouping options")
    @click.option("--date", default=None, help="The timestamp as YYYY-MM-DD HH:MM:SS")
    @click.argument("project", required=False)
    @click.argument("event", required=False)
    @click.argument("arguments", required=False)
    @click.pass_obj
    def Log(options, date, project, event, arguments):
        date = Command.ParseDate(date)
        print(options, date, project, event, arguments)
        # with SQLConnector(options.db) as c:
        # 	print (date)

    # =========================================================================
    # HELPERS / PARSERS
    # =========================================================================

    @classmethod
    def ParseDate(cls, text: str):
        """Extracts a date from the given text string."""
        return datetime.now()
        t = RE_SPACES.sub(" ", text.strip().lower())
        # NOW | YESTERDAY
        # LAST N? [DAY|WEEK|MONTH|YEAR]
        # N [DAY|WEEK|MONTH|YEAR](S)AGO
        # IN N [DAY|WEEK|MONTH|YEAR](S)
        if t == "now":
            return None
        elif t == "yesterday":
            return None
        elif "ago" in t:
            return None
        elif "in " in t:
            return None
        else:
            return dateutil.parser.parse(text)


# -----------------------------------------------------------------------------
#
# MAIN
#
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    Command.Run()

    # with SQLConnector() as c:
    # 	print (c.listEvents())

# EOF - vim
