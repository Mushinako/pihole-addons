# pihole-addons

Some script addon to pihole console commands. Note that these need to be run with necessary permissions to edit `gravity.db` (default in `/etc/pihole/gravity.db`)

Python versions under 3.5 are not tested and therefore not guaranteed to work.

You may need to restart the DNS server after running these commands (`pihole restartdns`). These scripts aim to provide command-line tools functionalities not provided by `pihole`, and therefore restarting DNS is not included.

Note: **Always backup your `gravity.db` before using this script or you may risk losing data!!!**

## What's this for

I tried to add some terminal automation tools to pihole.

## Files

### `toggle_domain.py`

Toggle enable/disable for the whitelists and/or blacklists of a domain

#### `toggle_domain.py` Help

```text
usage: toggle_domain.py [-h] [-b] [-w] domain {e,d,enable,disable}

Toggle enable/disable for a domain whitelist/blacklist

positional arguments:
  domain                domain/regex to be toggled
  {e,d,enable,disable}  enable/disable domain

optional arguments:
  -h, --help            show this help message and exit
  -b                    blacklist only
  -w                    whitelist only
```

#### `toggle_domain.py` Example

```bash
# Enable all whitelists and blacklists targeting domain "www.google.com"
python3 toggle_domain.py "www.google.com" e

# Disable all blacklists targeting regex "(\.|^)google\.com$"
python3 toggle_domain.py -b "(\.|^)google\.com$" d

# Invert all whitelists targeting regex "(\.|^)google\.com$"
python3 toggle_domain.py -w "(\.|^)google\.com$" t
```

### `toggle_group.py`

Toggle enable/disable for the whitelists and/or blacklists of domains in a group

Note: **This will toggle ALL domains in this group, even if it may also be in another group!**

#### `toggle_group.py` Help

```text
usage: toggle_group.py [-h] [-b] [-w] group {e,d,t,enable,disable,toggle}

Toggle enable/disable for domain whitelists/blacklists in a group

positional arguments:
  group                 group to be toggled
  {e,d,t,enable,disable,toggle}
                        enable/disable domains in the group

optional arguments:
  -h, --help            show this help message and exit
  -b                    blacklist only
  -w                    whitelist only
```

#### `toggle_group.py` Example

```bash
# Enable all whitelists and blacklists targeting group1
python3 toggle_group.py group1 e

# Disable all blacklists targeting group2
python3 toggle_group.py -b group2 d

# Invert all whitelists targeting group3
python3 toggle_group.py -w group3 t
```

### `update_group.py`

Edit the group(s) to which the whitelists and/or blacklists of a domain are assigned

#### `update_group.py` Help

```text
usage: update_group.py [-h] [-b] [-w] -g G [G ...] domain

Update group configuration for a domain whitelist/blacklist

positional arguments:
  domain        domain/regex to be assigned to the group(s)

optional arguments:
  -h, --help    show this help message and exit
  -b            blacklist only
  -w            whitelist only
  -g G [G ...]  groups to add the domain to
```

#### `update_group.py` Example

```bash
# Move all whitelists and blacklists targeting domain "www.google.com" to group1
python3 update_group.py "www.google.com" -g group1

# Move all blacklists targeting regex "(\.|^)google\.com$" to group2 and group3
python3 update_group.py -b "(\.|^)google\.com$" -g group2 group3
```
