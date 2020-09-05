#!/usr/bin/env python3
import sqlite3
from argparse import Namespace
from typing import List, Tuple, Dict

from db_utils import Domain, Group, db_sql

DOMAIN_LIST_READ_STMT = "SELECT * FROM domainlist"
GROUP_NAME_GET_STMT = "SELECT * FROM \"group\""


class CommonArgsDummy(Namespace):
    """Dummy class for argument object. Used only for type notation

    Properties:
        domain (str) : Domain/Regex name
        b      (bool): Whether blacklists will be processed
        w      (bool): Whether whitelists will be processed
    """

    def __init__(self) -> None:
        self.domain: str
        self.b: bool
        self.w: bool


def read_domains(conn: sqlite3.Connection, /) -> List[Domain]:
    """Read all blacklist and whitelist entries

    Arguments:
        conn [Positional] (sqlite3.Connection): Some connection to sqlite3 database

    Returns:
        time_removed (list[Domain]): List of `Domain` objects for each entry
    """

    cursor = db_sql(conn, DOMAIN_LIST_READ_STMT)
    all_domains: List[
        Tuple[int, int, str, int, int, int, str]
    ] = cursor.fetchall()
    time_removed = [Domain(domain) for domain in all_domains]
    return time_removed


def filter_domains(conn: sqlite3.Connection, /, args: CommonArgsDummy) -> List[Domain]:
    """Get all blacklist and whitelist entries corresponding to the command-line arguments

    Arguments:
        conn [Positional] (sqlite3.Connection): Some connection to sqlite3 database
        args              (argparse.Namespace): `argparse` result

    Returns:
        filtered_data (list[Domain]): List of `Domain` objects for each matching entry
    """

    domains = read_domains(conn)
    domain_data = [
        domain for domain in domains if domain.domain == args.domain
    ]
    if not domain_data:
        print(f"{args.domain} is not in domain list")
        return []
    if not args.b:
        filtered_data = [
            domain for domain in domain_data if domain.is_white]
    elif not args.w:
        filtered_data = [
            domain for domain in domain_data if domain.is_black]
    else:
        filtered_data = domain_data
    if not filtered_data:
        if not args.b:
            print(f"{args.domain} is not whitelisted")
        elif not args.w:
            print(f"{args.domain} is not blacklisted")
        else:
            print(f"{args.domain} is not in domain list")
        return []
    return filtered_data


def read_groups(conn: sqlite3.Connection, /) -> List[Group]:
    """Get all group entries

    Arguments:
        conn [Positional] (sqlite3.Connection): Some connection to sqlite3 database

    Returns:
        time_removed (list[Group]): List of `Group` objects for each entry
    """

    cursor = db_sql(conn, GROUP_NAME_GET_STMT)
    all_groups: List[Tuple[int, int, str, int, int, str]] = cursor.fetchall()
    time_removed = [Group(group) for group in all_groups]
    return time_removed


def get_group_names(conn: sqlite3.Connection, /) -> Dict[str, int]:
    """Get all group entry names

    Arguments:
        conn [Positional] (sqlite3.Connection): Some connection to sqlite3 database

    Returns:
        group_names (dict[str, int]): Dictionary mapping group name to group id
    """

    groups = read_groups(conn)
    group_names = {group.name: group.gid for group in groups}
    return group_names
