# ipnet

Simple IP subnet calculator using Python [ipaddress](https://docs.python.org/3/library/ipaddress.html) module, [Rich](https://github.com/Textualize/rich) and [Typer](https://github.com/fastapi/typer).

## Install as a UV tool

### 1. Install [UV](https://docs.astral.sh/uv/getting-started/installation/)

- Linux:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- Windows:
```
winget install --id=astral-sh.uv  -e
```

### 2. Install the script

```
uv tool install --from "git+https://github.com/tuirennder/ipnet" ipnet
```

## Usage

```
❯ ipnet --help

 Usage: ipnet [OPTIONS] COMMAND [ARGS]...

 IPv4 and IPv6 subnet calculator

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                             │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.      │
│ --help                        Show this message and exit.                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ examples   Show usage examples for all commands.                                                                    │
│ info       Display comprehensive subnet information for IPv4 and IPv6 networks.                                     │
│ split      Split a subnet into smaller subnets.                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

```
❯ ipnet info 2001:1:2:3::0/64
╭─ Network Information: 2001:1:2:3::/64 ────────────────────────────────────────────────────────────────╮
│                                                                                                       │
│  Version:    IPv6                                                                                     │
│  Addresses:  1.84467E+19                                                                              │
│  Subnet:     2001:1:2:3::/64                                                                          │
│  Netmask:    ffff:ffff:ffff:ffff::                                                                    │
│  Hostmask:   ::ffff:ffff:ffff:ffff                                                                    │
│  Expanded:   2001:0001:0002:0003:0000:0000:0000:0000/64                                               │
│  Network:    2001:1:2:3::                                                                             │
│  Broadcast:  2001:1:2:3:ffff:ffff:ffff:ffff                                                           │
│  Hosts:      2001:1:2:3::1 to 2001:1:2:3:ffff:ffff:ffff:fffe                                          │
│  Flags:      PRIVATE                                                                                  │
│                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
```
❯ ipnet split 2001:1:2:3::0/64 --count 16
╭─ Total: 16 subnets ───────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                       │
│  ╭──────────────────────┬──────────────┬──────────────────────────────────────────────────────╮       │
│  │ Prefixes             │ Nbr of hosts │ Range of hosts                                       │       │
│  ├──────────────────────┼──────────────┼──────────────────────────────────────────────────────┤       │
│  │ 2001:1:2:3::/68      │ 1.15292E+18  │ 2001:1:2:3::1 to 2001:1:2:3:fff:ffff:ffff:fffe       │       │
│  │ 2001:1:2:3:1000::/68 │ 1.15292E+18  │ 2001:1:2:3:1000::1 to 2001:1:2:3:1fff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:2000::/68 │ 1.15292E+18  │ 2001:1:2:3:2000::1 to 2001:1:2:3:2fff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:3000::/68 │ 1.15292E+18  │ 2001:1:2:3:3000::1 to 2001:1:2:3:3fff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:4000::/68 │ 1.15292E+18  │ 2001:1:2:3:4000::1 to 2001:1:2:3:4fff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:5000::/68 │ 1.15292E+18  │ 2001:1:2:3:5000::1 to 2001:1:2:3:5fff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:6000::/68 │ 1.15292E+18  │ 2001:1:2:3:6000::1 to 2001:1:2:3:6fff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:7000::/68 │ 1.15292E+18  │ 2001:1:2:3:7000::1 to 2001:1:2:3:7fff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:8000::/68 │ 1.15292E+18  │ 2001:1:2:3:8000::1 to 2001:1:2:3:8fff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:9000::/68 │ 1.15292E+18  │ 2001:1:2:3:9000::1 to 2001:1:2:3:9fff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:a000::/68 │ 1.15292E+18  │ 2001:1:2:3:a000::1 to 2001:1:2:3:afff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:b000::/68 │ 1.15292E+18  │ 2001:1:2:3:b000::1 to 2001:1:2:3:bfff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:c000::/68 │ 1.15292E+18  │ 2001:1:2:3:c000::1 to 2001:1:2:3:cfff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:d000::/68 │ 1.15292E+18  │ 2001:1:2:3:d000::1 to 2001:1:2:3:dfff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:e000::/68 │ 1.15292E+18  │ 2001:1:2:3:e000::1 to 2001:1:2:3:efff:ffff:ffff:fffe │       │
│  │ 2001:1:2:3:f000::/68 │ 1.15292E+18  │ 2001:1:2:3:f000::1 to 2001:1:2:3:ffff:ffff:ffff:fffe │       │
│  ╰──────────────────────┴──────────────┴──────────────────────────────────────────────────────╯       │
│                                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────╯
```