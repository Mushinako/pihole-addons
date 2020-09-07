#!/usr/bin/env python3
"""Common functions"""

import sqlite3
from argparse import Namespace
from typing import List, Tuple, Dict, Set

from .db_utils import Domain, Group, db_sql

DOMAIN_LIST_GET_STMT = "SELECT * FROM domainlist"
GROUP_NAME_GET_STMT = "SELECT * FROM \"group\""
DOMAIN_GROUP_CORR_GET_STMT = "SELECT * FROM domainlist_by_group"


class CommonArgsDummy(Namespace):
    """Dummy class for argument object. Used only for type notation

    Properties:
        b      (bool): Whether blacklists will be processed
        w      (bool): Whether whitelists will be processed
    """

    def __init__(self) -> None:
        self.b: bool
        self.w: bool


class DomainCommonArgsDummy(CommonArgsDummy):
    """Dummy class for argument object for domain name processing.
    Used only for type notation

    Properties:
        domain (str) : Domain/Regex name
        b      (bool): Whether blacklists will be processed
        w      (bool): Whether whitelists will be processed
    """

    def __init__(self) -> None:
        self.domain: str


class IDCommonArgsDummy(CommonArgsDummy):
    """Dummy class for argument object for domain id processing.
    Used only for type notation

    Properties:
        ids_ (set[int]): Domain/Regex ID
        b    (bool)    : Whether blacklists will be processed
        w    (bool)    : Whether whitelists will be processed
    """

    def __init__(self) -> None:
        self.ids_: Set[int]


def filter_domains_by_name(conn: sqlite3.Connection, args: DomainCommonArgsDummy) -> List[Domain]:
    """Get all blacklist and/or whitelist entries corresponding to the command-line arguments

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database
        args (argparse.Namespace): `argparse` result

    Returns:
        filtered_data (list[Domain]): List of `Domain` objects for each matching entry
    """

    domains = get_domains(conn)
    domain_data = [
        domain for domain in domains if domain.domain == args.domain
    ]
    if not domain_data:
        print(f"{args.domain} is not in domain list")
        return []
    filtered_data = filter_domains_by_blackwhite(domain_data, args)
    return filtered_data


def filter_domains_by_id(conn: sqlite3.Connection, args: IDCommonArgsDummy) -> List[Domain]:
    """Get all blacklist and/or whitelist entries corresponding to the command-line arguments

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database
        args (argparse.Namespace): `argparse` result

    Returns:
        filtered_data (list[Domain]): List of `Domain` objects for each matching entry
    """

    domains = get_domains(conn)
    domain_data = [domain for domain in domains if domain.id_ in args.ids_]
    if not domain_data:
        print(f"Domains #{args.ids_} are not in domain list")
        return []
    filtered_data = filter_domains_by_blackwhite(domain_data, args)
    return filtered_data


def filter_domains_by_blackwhite(domains: List[Domain], args: CommonArgsDummy) -> List[Domain]:
    """Get all blacklist and/or whitelist entries corresponding to the command-line arguments

    Arguments:
        domains (list[Domain])      : A list of `Domain` objects
        args    (argparse.Namespace): `argparse` result

    Returns:
        filtered_data (list[Domain]): List of `Domain` objects for each matching entry
    """
    if not args.b:
        filtered_data = [domain for domain in domains if domain.is_white]
    elif not args.w:
        filtered_data = [domain for domain in domains if domain.is_black]
    else:
        filtered_data = domains
    if not filtered_data:
        if not args.b:
            print(f"{args.domain} is not whitelisted")
        elif not args.w:
            print(f"{args.domain} is not blacklisted")
        else:
            print(f"{args.domain} is not in domain list")
        return []
    return filtered_data


def get_domains(conn: sqlite3.Connection) -> List[Domain]:
    """Read all blacklist and whitelist entries

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database

    Returns:
        time_removed (list[Domain]): List of `Domain` objects for each entry
    """

    cursor = db_sql(conn, DOMAIN_LIST_GET_STMT)
    all_domains: List[
        Tuple[int, int, str, int, int, int, str]
    ] = cursor.fetchall()
    time_removed = [Domain(domain) for domain in all_domains]
    return time_removed


def get_groups(conn: sqlite3.Connection) -> List[Group]:
    """Get all group entries

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database

    Returns:
        time_removed (list[Group]): List of `Group` objects for each entry
    """

    cursor = db_sql(conn, GROUP_NAME_GET_STMT)
    all_groups: List[Tuple[int, int, str, int, int, str]] = cursor.fetchall()
    time_removed = [Group(group) for group in all_groups]
    return time_removed


def get_group_names(conn: sqlite3.Connection) -> Dict[str, int]:
    """Get all group entry names

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database

    Returns:
        group_names (dict[str, int]): Dictionary mapping group name to group id
    """

    groups = get_groups(conn)
    group_names = {group.name: group.gid for group in groups}
    return group_names


def get_domain_ids_by_group_ids(conn: sqlite3.Connection, gid: int) -> Set[int]:
    """Get IDs of domains under a group by Group ID

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database
        gid  (int)               : Group ID

    Returns:
        domain_ids (set[int]): Set of Domain IDs in the group
    """
    cursor = db_sql(conn, DOMAIN_GROUP_CORR_GET_STMT)
    all_corr: List[Tuple[int, int]] = cursor.fetchall()
    domain_ids = {
        domain_id for domain_id, group_id in all_corr if group_id == gid
    }
    return domain_ids
