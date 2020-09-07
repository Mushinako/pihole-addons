#!/usr/bin/env python3
"""Runs `update_group` based on Python version"""

import sys

major, minor, _, _, _ = sys.version_info

if major < 3:
    print("Python 2 and below are not supported")
    sys.exit(23)
if minor < 5:
    print("W: Python 3.4 and below are not tested. Errors may occur")
if minor < 7:
    from p35.update_group import main
else:
    from p37.update_group import main


def tmain() -> None:
    args = sys.argv[1:]
    main(args)


if __name__ == "__main__":
    tmain()
