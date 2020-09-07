#!/usr/bin/env python3
"""sqlite3 database utility functions"""

import sqlite3
import os.path
from io import TextIOWrapper
from configparser import ConfigParser, NoOptionError
from contextlib import contextmanager
from typing import Iterable, Tuple

INI_PATH = "/etc/pihole/pihole-FTL.conf"
DB_PATH_KEY = "GRAVITYDB"
DEFAULT_DB_PATH = "/etc/pihole/gravity.db"
DUMMY_HEAD = "DummyHead"


class FakeIniHeader:
    """Pihole config wrapper. Adds dummy section head that `ConfigParser`
    requires

    Properties:
        file      (io.TextIOWrapper): The actual file hander
        head_read (bool)            : Whether the section head is read
    """

    def __init__(self, file: TextIOWrapper) -> None:
        self.file = file
        self.head_read: bool

    def __iter__(self) -> str:
        self.head_read = False
        return self

    def __next__(self) -> str:
        if not self.head_read:
            self.head_read = True
            return f"[{DUMMY_HEAD}]\n"
        line = self.file.readline()
        if not line:
            raise StopIteration
        return line


# Read `pihole` config to see if there's an alternative path
#   for `gravity.db`
if not os.path.isfile(INI_PATH):
    DB_PATH = DEFAULT_DB_PATH
else:
    config = ConfigParser()
    with open(INI_PATH, "r") as f:
        ini_file = iter(FakeIniHeader(f))
        config.read_file(ini_file)
    try:
        DB_PATH = config.get(DUMMY_HEAD, DB_PATH_KEY)
    except NoOptionError:
        DB_PATH = DEFAULT_DB_PATH

# Map type number to respective nicknames
#   0 -> "white" and so on
TYPE_MAP = ["white", "black", "white_re", "black_re"]


class Domain:
    """Dataclass for domain whitelist/blacklist entry

    Properties:
        id_            (int) : ID of this entry
        type_          (int) : Entry type (black/white; exact/regex)
        domain         (str) : Domain/Regex value
        enabled        (int) : 1 for enabled, 0 for disabled
        comment        (str) : Comment
        type_str [get] (str) : Type string corresponding to `self.type_`
        is_white [get] (bool): Whether the entry is a whitelist
        is_black [get] (bool): Whether the entry is a blacklist
    """

    def __init__(self, domain: Tuple[int, int, str, int, int, int, str]) -> None:
        self.id_, self.type_, self.domain, self.enabled, _, _, self.comment = domain

    @property
    def type_str(self) -> str:
        return TYPE_MAP[self.type_]

    @property
    def is_white(self) -> bool:
        return "white" in self.type_str

    @property
    def is_black(self) -> bool:
        return "black" in self.type_str


class Group:
    """Dataclass for group

    Properties:
        gid     (int): Group ID
        enabled (int): 1 for enabled, 0 for disabled
        name    (str): Group name
        comment (str): Comment
    """

    def __init__(self, group: Tuple[int, int, str, int, int, str]) -> None:
        self.gid, self.enabled, self.name, _, _, self.comment = group


@contextmanager
def open_gravity():
    """Context manager wrapper for `gravity.db` connection

    Yields:
        conn (sqlite3.Connection): The connection to `gravity.db`
    """

    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def db_sql(conn: sqlite3.Connection, sql: str) -> sqlite3.Cursor:
    """Run SQL command without preparation

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database
        sql  (str)               : SQL command

    Returns:
        cursor (sqlite3.Cursor): Cursor returned by SQL execution
    """

    with conn:
        cursor = conn.execute(sql)
    return cursor


def db_sql_prepare_single(conn: sqlite3.Connection, sql: str, parameters: Iterable) -> sqlite3.Cursor:
    """Run SQL command with single command preparation

    Arguments:
        conn       (sqlite3.Connection): Some connection to sqlite3 database
        sql        (str)               : SQL command template
        parameters (Iterable)          : Parameters for the SQL command template

    Returns:
        cursor (sqlite3.Cursor): Cursor returned by SQL execution
    """

    with conn:
        cursor = conn.execute(sql, parameters)
    return cursor


def db_sql_prepare_multiple(conn: sqlite3.Connection, sql: str, parameters: Iterable[Iterable]) -> sqlite3.Cursor:
    """Run similar SQL commands, each with command preparation

    Arguments:
        conn       (sqlite3.Connection): Some connection to sqlite3 database
        sql        (str)               : SQL command template
        parameters (Iterable[Iterable]): List of parameters for the SQL command template

    Returns:
        cursor (sqlite3.Cursor): Cursor returned by SQL execution
    """

    with conn:
        cursor = conn.executemany(sql, parameters)
    return cursor
