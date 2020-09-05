#!/usr/bin/env python3
import argparse

from .db_utils import open_gravity, db_sql_prepare_single, db_sql_prepare_multiple
from .get_data import filter_domains, get_group_names

GROUP_REMOVE_STMT = "DELETE FROM domainlist_by_group WHERE domainlist_id = ?"
GROUP_INSERT_STMT = "INSERT INTO domainlist_by_group (domainlist_id, group_id) VALUES (?, ?)"


def update_db(conn, id_, groups):
    """Do the update in database

    Arguments:
        conn [Positional] (sqlite3.Connection): Some connection to sqlite3 database
        id_               (int)               : ID of whitelist/blacklist entry
        domains           (Iterable[int])     : List of group IDs to which the entry is moved
    """

    db_sql_prepare_single(conn, GROUP_REMOVE_STMT, (id_,))
    insert_parameters = [(id_, gid) for gid in groups]
    db_sql_prepare_multiple(conn, GROUP_INSERT_STMT, insert_parameters)


def parse_args(argv):
    """Parse command-line arguments

    Arguments:
        argv (list[str]): Args from command-line

    Returns:
        args (argparse.Namespace): Parsed arguments
    """

    parser = argparse.ArgumentParser(
        description="Update group configuration for a domain whitelist/blacklist"
    )
    parser.add_argument(
        "domain",
        help="domain/regex to be assigned to the group(s)"
    )
    parser.add_argument(
        "-b",
        action="store_true",
        help="blacklist only"
    )
    parser.add_argument(
        "-w",
        action="store_true",
        help="whitelist only"
    )
    parser.add_argument(
        "-g",
        nargs="+",
        required=True,
        help="groups to add the domain to"
    )
    args = parser.parse_args(argv)
    if not args.b and not args.w:
        args.b = args.w = True
    return args


def main(argv):
    """Main function for `update_group`

    Arguments:
        argv (list[str]): Args from command-line
    """
    args = parse_args(argv)
    with open_gravity() as conn:
        groups = get_group_names(conn)
        group_ids = set()
        for g in args.g:
            if g not in groups:
                print("{} is not a valid group name".format(g))
                return
            group_ids.add(groups[g])
        filtered_data = filter_domains(conn, args)
        if not filtered_data:
            return
        for domain in filtered_data:
            update_db(conn, domain.id_, group_ids)


if __name__ == "__main__":
    main()
