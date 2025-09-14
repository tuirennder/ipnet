# Copilot Instructions for this repo

This project is a single-file Typer CLI that prints richly formatted IPv4/IPv6 subnet info and splits networks. It targets Python 3.13+ and is optimized for the `uv` workflow.

## Big picture
- Main entrypoint and logic live in `ipnet.py`.
- CLI is built with Typer; UI is rendered with Rich. No services/DB; all pure stdlib + Rich/Typer.
- Core object: `SubnetCalculator` (formatting + calculations). Commands call its methods; they do not print raw strings directly.
- Errors are routed through `ErrorHandler.print_error(...)` and then `raise typer.Exit(1)` to keep UX consistent.

## How to run
- One-off with uv (recommended; uses inline script metadata):
  - Make executable once: `chmod +x ipnet.py`
  - Run: `./ipnet.py --help`, `./ipnet.py examples`, `./ipnet.py info 172.16.0.1/21`
- Without uv (ensure deps installed): `python ipnet.py --help`
- Installed console script (from `pyproject.toml`): `ipnet --help` (entry point maps to `ipnet:app`).

## File structure and roles
- `ipnet.py`
  - Typer app: `app = typer.Typer(rich_markup_mode="rich")`
  - Commands:
    - `examples` → shows curated Rich examples panel
    - `info` → `parse_network_input(...)` → `SubnetCalculator.display_subnet_info(...)`
    - `split` → validates exactly one of `--count` or `--mask` → calls `split_subnet_by_count|prefix`
  - UI/UX:
    - Rich grid + panels; constants: `DEFAULT_TABLE_STYLE`, `HOST_COUNT_STYLE`, `HOST_RANGE_STYLE`
    - `MAX_DISPLAYED_SUBNETS` caps rows and appends an overflow message panel
    - `create_python_info_panel(...)` renders env + uv/venv detection
  - Parsing: `parse_network_input(prefix, mask=None)` accepts `ip/mask` or separate `mask` (CIDR or dotted)
  - Flags shown for a network: `MCAST, PRIVATE, GLOBAL, UNSPECIFIED, RESERVED, LOOPBACK, LINK_LOCAL`
- `pyproject.toml`
  - Python: `>=3.13`; deps: `rich`, `typer`; build backend: Hatchling
  - Console script: `ipnet = "ipnet:app"` (keep `app` at module top-level)

## Conventions to follow
- Always surface user-facing errors via `ErrorHandler.print_error(title, message, suggestion)` then `typer.Exit(1)`; don’t `print()` or `sys.exit()` directly in commands.
- Prefer Rich components (Table.grid, Panel, Text) and reuse the styling constants. Avoid ad-hoc color strings.
- Keep command args/options typed with `typing.Annotated` + Typer help text for consistent `--help` output.
- For large listings, respect `MAX_DISPLAYED_SUBNETS` and show a dim overflow note.
- When adding dependencies for uv one-off runs, update the inline uv script block at the top of `ipnet.py` (between `# /// script` and `# ///`) and mirror in `pyproject.toml`.

## Extending the CLI (patterns)
- New command: decorate a function with `@app.command()`; parse inputs with helpers (e.g., `parse_network_input`) and delegate to a method on `SubnetCalculator` or a new small class.
- New output: build a Rich `Table`/`Panel` and wrap it via the same border/box styles so it matches existing UI.
- Input validation: validate early, then use `ErrorHandler` + `typer.Exit(1)` with an actionable suggestion message.
- Packaging: if you split `ipnet.py` into a package/module, update `[project.scripts].ipnet` accordingly (still point to `:app`).

## Typical developer flows
- Local dev via uv: edit `ipnet.py` → `./ipnet.py examples` or `./ipnet.py info 2001:db8::/64`
- Install and run as a tool: `pip install .` (or `uv pip install .`) → `ipnet ...`
- Manual smoke tests (no test suite in repo):
  - `info`: IPv4 `/24`, `/31`, `/32` and IPv6 `/64`, `/127`, `/128`
  - `split`: with `--mask` and with `--count`; verify overflow message when rows > `MAX_DISPLAYED_SUBNETS`
