#!/usr/bin/env python3
"""usage: toggle_group.py [-h] [-b] [-w] group {e,d,t,enable,disable,toggle}

Toggle enable/disable for domain whitelists/blacklists in a group

positional arguments:
  group                 group to be toggled
  {e,d,t,enable,disable,toggle}
                        enable/disable domains in the group

optional arguments:
  -h, --help            show this help message and exit
  -b                    blacklist only
  -w                    whitelist only
"""

import argparse
from sqlite3 import Connection
from dataclasses import dataclass
from typing import Tuple, List, Set

from .db_utils import Domain, open_gravity, db_sql_prepare_multiple
from .get_data import CommonArgsDummy, filter_domains_by_id, get_domain_ids_by_group_ids, get_group_names

DOMAIN_TOGGLE_STMT = "UPDATE domainlist SET enabled = ?, comment = ?, type = ? WHERE id = ?"


class ToggleGroupArgs(CommonArgsDummy):
    """Dummy class for argument object. Used only for type notation

    Properties:
        group  (str) : Group name
        toggle (str) : Toggle to enable/disable
        b      (bool): Whether blacklists will be processed
        w      (bool): Whether whitelists will be processed
        t      (int) : 1 for enable; 0 for disable; -1 for toggle
    """

    def __init__(self) -> None:
        self.group: str
        self.toggle: str
        self.t: int


@dataclass
class FilterDomainByIDArgs:
    """Args class for argument object for domain id processing

    Properties:
        ids_ (set[int]): Domain/Regex IDs
        b    (bool)    : Whether blacklists will be processed
        w    (bool)    : Whether whitelists will be processed
    """
    ids_: Set[int]
    b: bool
    w: bool


def update_db(conn: Connection, domains: List[Domain]) -> None:
    """Do the update in database

    Arguments:
        conn    (sqlite3.Connection): Some connection to sqlite3 database
        domains (list[Domain])      : List of `Domain` objects for each entry
    """

    update_parameters: Tuple[int, str, int, int] = [(
        domain.enabled ^ 1, domain.comment, domain.type_, domain.id_
    ) for domain in domains]
    db_sql_prepare_multiple(conn, DOMAIN_TOGGLE_STMT, update_parameters)


def parse_args(argv: List[str]) -> ToggleGroupArgs:
    """Parse command-line arguments

    Arguments:
        argv (list[str]): Args from command-line

    Returns:
        args (argparse.Namespace): Parsed arguments
    """

    parser = argparse.ArgumentParser(
        description="Toggle enable/disable for domain whitelists/blacklists in a group"
    )
    parser.add_argument(
        "group",
        help="group to be toggled"
    )
    parser.add_argument(
        "toggle",
        choices=("e", "d", "t", "enable", "disable", "toggle"),
        help="enable/disable domains in the group"
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
    args = parser.parse_args(argv, namespace=ToggleGroupArgs())
    if not args.b and not args.w:
        args.b = args.w = True
    if args.toggle in ("t", "toggle"):
        args.t = -1
    else:
        args.t = int(args.toggle in ("e", "enable"))
    return args


def main(argv: List[str]) -> None:
    """Main function for `toggle_domain`

    Arguments:
        argv (list[str]): Args from command-line
    """
    args = parse_args(argv)
    with open_gravity() as conn:
        groups = get_group_names(conn)
        if args.group not in groups:
            print(f"{args.group} is not a valid group name")
            return
        group_id = groups[args.group]
        domain_ids = get_domain_ids_by_group_ids(conn, group_id)
        if not domain_ids:
            print(f"No domains are in group {args.group}")
            return
        new_args = FilterDomainByIDArgs(domain_ids, args.b, args.w)
        filtered_data = filter_domains_by_id(conn, new_args)
        if not filtered_data:
            return
        if args.t == -1:
            domains_2_change = filtered_data
        else:
            domains_2_change = [
                domain for domain in filtered_data if domain.enabled != args.t
            ]
        update_db(conn, domains_2_change)
