#!/usr/bin/env python3
import argparse

from db_utils import open_gravity, db_sql_prepare_multiple
from get_data import filter_domains

DOMAIN_TOGGLE_STMT = "UPDATE domainlist SET enabled = ?, comment = ?, type = ? WHERE id = ?"


def update_db(conn, domains):
    """Do the update in database

    Arguments:
        conn [Positional] (sqlite3.Connection): Some connection to sqlite3 database
        domains           (list[Domain])      : List of `Domain` objects for each entry
    """

    update_parameters = [(
        domain.enabled ^ 1, domain.comment, domain.type_, domain.id_
    ) for domain in domains]
    db_sql_prepare_multiple(conn, DOMAIN_TOGGLE_STMT, update_parameters)


def parse_args():
    """Parse command-line arguments

    Returns:
        args (argparse.Namespace): Parsed arguments
    """

    parser = argparse.ArgumentParser(
        description="Toggle enable/disable for a domain whitelist/blacklist"
    )
    parser.add_argument(
        "domain",
        help="domain/regex to be toggled"
    )
    parser.add_argument(
        "toggle",
        choices=("e", "d", "enable", "disable"),
        help="enable/disable domain"
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
    args = parser.parse_args()
    if not args.b and not args.w:
        args.b = args.w = True
    args.t = int(args.toggle in ("e", "enable"))
    return args


def main():
    """Main function for `toggle_domain`"""
    args = parse_args()
    with open_gravity() as conn:
        filtered_data = filter_domains(conn, args)
        if not filtered_data:
            return
        domains_2_change = [
            domain for domain in filtered_data if domain.enabled != args.t
        ]
        update_db(conn, domains_2_change)


if __name__ == "__main__":
    main()
