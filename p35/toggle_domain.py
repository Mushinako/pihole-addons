#!/usr/bin/env python3
"""usage: toggle_domain.py [-h] [-b] [-w] domain {e,d,enable,disable}

Toggle enable/disable for a domain whitelist/blacklist

positional arguments:
  domain                domain/regex to be toggled
  {e,d,enable,disable}  enable/disable domain

optional arguments:
  -h, --help            show this help message and exit
  -b                    blacklist only
  -w                    whitelist only
"""

import argparse

from .db_utils import open_gravity, db_sql_prepare_multiple
from .get_data import filter_domains

DOMAIN_TOGGLE_STMT = "UPDATE domainlist SET enabled = ?, comment = ?, type = ? WHERE id = ?"


def update_db(conn, domains):
    """Do the update in database

    Arguments:
        conn    (sqlite3.Connection): Some connection to sqlite3 database
        domains (list[Domain])      : List of `Domain` objects for each entry
    """

    update_parameters = [(
        domain.enabled ^ 1, domain.comment, domain.type_, domain.id_
    ) for domain in domains]
    db_sql_prepare_multiple(conn, DOMAIN_TOGGLE_STMT, update_parameters)


def parse_args(argv):
    """Parse command-line arguments

    Arguments:
        argv (list[str]): Args from command-line

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
        choices=("e", "d", "t", "enable", "disable", "toggle"),
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
    args = parser.parse_args(argv)
    if not args.b and not args.w:
        args.b = args.w = True
    if args.toggle in ("t", "toggle"):
        args.t = -1
    else:
        args.t = int(args.toggle in ("e", "enable"))
    return args


def main(argv):
    """Main function for `toggle_domain`

    Arguments:
        argv (list[str]): Args from command-line
    """
    args = parse_args(argv)
    with open_gravity() as conn:
        filtered_data = filter_domains(conn, args)
        if not filtered_data:
            return
        if args.t == -1:
            domains_2_change = filtered_data
        else:
            domains_2_change = [
                domain for domain in filtered_data if domain.enabled != args.t
            ]
        update_db(conn, domains_2_change)
