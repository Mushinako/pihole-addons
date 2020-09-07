#!/usr/bin/env python3
"""Common functions"""

from .db_utils import Domain, Group, db_sql

DOMAIN_LIST_GET_STMT = "SELECT * FROM domainlist"
GROUP_NAME_GET_STMT = "SELECT * FROM \"group\""
DOMAIN_GROUP_CORR_GET_STMT = "SELECT * FROM domainlist_by_group"


def filter_domains_by_name(conn, args):
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
        print("{} is not in domain list".format(args.domain))
        return []
    filtered_data = filter_domains_by_blackwhite(domain_data, args)
    return filtered_data


def filter_domains_by_id(conn, args):
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
        print("Domains #{} are not in domain list".format(args.ids_))
        return []
    filtered_data = filter_domains_by_blackwhite(domain_data, args)
    return filtered_data


def filter_domains_by_blackwhite(domains, args):
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
            print("{} is not whitelisted".format(args.domain))
        elif not args.w:
            print("{} is not blacklisted".format(args.domain))
        else:
            print("{} is not in domain list".format(args.domain))
        return []
    return filtered_data


def get_domains(conn):
    """Read all blacklist and whitelist entries

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database

    Returns:
        time_removed (list[Domain]): List of `Domain` objects for each entry
    """

    cursor = db_sql(conn, DOMAIN_LIST_GET_STMT)
    all_domains = cursor.fetchall()
    time_removed = [Domain(domain) for domain in all_domains]
    return time_removed


def get_groups(conn):
    """Get all group entries

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database

    Returns:
        time_removed (list[Group]): List of `Group` objects for each entry
    """

    cursor = db_sql(conn, GROUP_NAME_GET_STMT)
    all_groups = cursor.fetchall()
    time_removed = [Group(group) for group in all_groups]
    return time_removed


def get_group_names(conn):
    """Get all group entry names

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database

    Returns:
        group_names (dict[str, int]): Dictionary mapping group name to group id
    """

    groups = get_groups(conn)
    group_names = {group.name: group.gid for group in groups}
    return group_names


def get_domain_ids_by_group_ids(conn, gid):
    """Get IDs of domains under a group by Group ID

    Arguments:
        conn (sqlite3.Connection): Some connection to sqlite3 database
        gid  (int)               : Group ID

    Returns:
        domain_ids (set[int]): Set of Domain IDs in the group
    """
    cursor = db_sql(conn, DOMAIN_GROUP_CORR_GET_STMT)
    all_corr = cursor.fetchall()
    domain_ids = {
        domain_id for domain_id, group_id in all_corr if group_id == gid
    }
    return domain_ids
