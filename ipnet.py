#!/usr/bin/env -S uv run --script
"""
IPv4 and IPv6 subnet calculator with Rich styling and Typer CLI.

How to use:
- install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
- make the script executable and run directly: chmod +x ipnet.py; ./ipnet.py --help
"""

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "rich>=14.1.0",
#     "typer>=0.9.0",
# ]
# ///

import ipaddress
import math
import os
import sys
from dataclasses import dataclass
from typing import Optional, Annotated

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.traceback import install

# Install Rich traceback handler for better error display
install(show_locals=True, suppress=[typer])

if sys.version_info.major < 3:
    raise SystemExit(
        f"Error: Python 3 required.\nCurrent Python version: {sys.version}"
    )


# Constants
MAX_DISPLAYED_SUBNETS = 50
DEFAULT_TABLE_STYLE = "cyan3"
HOST_COUNT_STYLE = "magenta3"
HOST_RANGE_STYLE = "gold1"


class ErrorHandler:
    """Centralized error handling with Rich formatting."""

    def __init__(self):
        self.error_console = Console(stderr=True)
        # self.console = Console()

    def print_error(
        self, title: str, message: str, suggestion: Optional[str] = None
    ) -> None:
        error_text = Text()
        error_text.append(f"{message}", style="bold red")

        if suggestion:
            error_text.append(f"\n\n{suggestion}", style="dim yellow")

        error_panel = Panel(
            error_text,
            title=f"{title}",
            title_align="left",
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 2),
            expand=False,
        )

        self.error_console.print(error_panel)

    def print_exception(
        self, exc: Exception, context: str = "An error occurred"
    ) -> None:
        """Print exception with traceback."""
        self.error_console.print_exception(show_locals=True)

        # Also show a user-friendly error panel
        self.print_error(
            context, str(exc), "Check your input parameters and try again."
        )


# Global error handler instance
error_handler = ErrorHandler()


def get_execution_environment() -> dict[str, str]:
    """
    Detect the Python execution environment and return information about it.

    https://stackoverflow.com/questions/1871549/how-to-determine-if-python-is-running-inside-a-virtualenv

    Returns:
        dict: Contains environment type, python version, and path information
    """
    env_info = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_executable": sys.executable,
        "environment_type": "system",
        "environment_path": None,
        "in_virtual_env": False,
    }

    # Check for virtual environment using sys.prefix comparison (most reliable)
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        env_info["in_virtual_env"] = True
        env_info["environment_type"] = "virtualenv"
        env_info["environment_path"] = sys.prefix

    # Check for VIRTUAL_ENV environment variable (set by activate scripts)
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if virtual_env:
        env_info["environment_path"] = virtual_env
        if not env_info["in_virtual_env"]:
            env_info["in_virtual_env"] = True
            env_info["environment_type"] = "venv"

    # Check if we're running with uv (look for uv in executable path or environment)
    if "uv" in sys.executable.lower() or os.environ.get("UV_PROJECT_ENVIRONMENT"):
        env_info["environment_type"] = "uv"

    return env_info


@dataclass
class TableConfig:
    """Configuration for Rich table styling."""

    border_style: str = DEFAULT_TABLE_STYLE
    title_style: str = f"italic {DEFAULT_TABLE_STYLE}"
    box_style = box.ROUNDED
    title_justify: str = "center"


class SubnetCalculator:
    """IPv4/IPv6 subnet calculator with Rich formatting."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.table_config = TableConfig()

    def display_subnet_info(
        self, network: ipaddress.IPv4Network | ipaddress.IPv6Network
    ) -> None:
        """Display comprehensive subnet information in a Rich panel."""
        # Create main info table
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(style="bold cyan", no_wrap=True)
        info_table.add_column(style="white")

        # Basic network information
        info_table.add_row("Version:", f"[bold magenta]IPv{network.version}[/]")
        info_table.add_row("Addresses:", f"[bold yellow]{network.num_addresses:,G}[/]")
        info_table.add_row("Subnet:", f"[bold green]{network.with_prefixlen}[/]")
        info_table.add_row("Netmask:", f"{network.netmask}")
        info_table.add_row("Hostmask:", f"{network.hostmask}")

        # IPv6 specific information
        if network.version == 6:
            info_table.add_row("Expanded:", f"[dim]{network.exploded}[/]")

        # Network addresses
        info_table.add_row("Network:", f"[bold blue]{network.network_address}[/]")
        info_table.add_row("Broadcast:", f"[bold blue]{network.broadcast_address}[/]")

        # Host range display based on network size
        if network.num_addresses == 1:
            # /32 and /128
            info_table.add_row("Host:", f"[bold cyan]{network[0]}[/]")
        elif network.num_addresses == 2:
            # /31 and /127
            info_table.add_row(
                "Hosts:", f"[bold cyan]{network[0]}[/] to [bold cyan]{network[1]}[/]"
            )
        else:
            host_start = network.network_address + 1
            host_end = network.broadcast_address - 1
            info_table.add_row(
                "Hosts:", f"[bold cyan]{host_start}[/] to [bold cyan]{host_end}[/]"
            )

        # IPv4 hexadecimal representation
        if network.version == 4:
            info_table.add_row(
                "Hexadecimal:", f"[bold yellow]{int(network.network_address):X}[/]"
            )

        # Network flags with color coding
        flags = self._get_network_flags(network)
        if flags:
            colored_flags = []
            for flag in flags:
                if flag == "PRIVATE":
                    colored_flags.append(f"[green]{flag}[/]")
                elif flag == "GLOBAL":
                    colored_flags.append(f"[blue]{flag}[/]")
                elif flag == "LOOPBACK":
                    colored_flags.append(f"[yellow]{flag}[/]")
                elif flag in ["MCAST", "RESERVED"]:
                    colored_flags.append(f"[red]{flag}[/]")
                else:
                    colored_flags.append(f"[dim]{flag}[/]")
            info_table.add_row("Flags:", " ".join(colored_flags))

        # Create the panel with the info table
        panel_title = f"Network Information: {network.with_prefixlen}"
        panel = Panel(
            info_table,
            title=panel_title,
            title_align="left",
            border_style="bright_blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def _get_network_flags(
        self, network: ipaddress.IPv4Network | ipaddress.IPv6Network
    ) -> list[str]:
        """Get list of network flags."""
        flags = []
        if network.is_multicast:
            flags.append("MCAST")
        if network.is_private:
            flags.append("PRIVATE")
        if network.is_global:
            flags.append("GLOBAL")
        if network.is_unspecified:
            flags.append("UNSPECIFIED")
        if network.is_reserved:
            flags.append("RESERVED")
        if network.is_loopback:
            flags.append("LOOPBACK")
        if network.is_link_local:
            flags.append("LINK_LOCAL")
        return flags

    def _create_subnet_table(self, total_subnets: int) -> Table:
        """Create a Rich table for subnet display."""
        table = Table(
            box=self.table_config.box_style,
            border_style=self.table_config.border_style,
            show_header=True,
        )

        table.add_column("Prefixes", style=DEFAULT_TABLE_STYLE, no_wrap=True)
        table.add_column("Nbr of hosts", justify="center", style=HOST_COUNT_STYLE)
        table.add_column("Range of hosts", justify="left", style=HOST_RANGE_STYLE)

        return table

    def _display_subnet_table_in_panel(
        self, table: Table, total_subnets: int, overflow_message: Optional[str] = None
    ) -> None:
        """Display the subnet table wrapped in a Rich panel."""
        from rich.console import Group

        # Create panel with the table
        panel_title = f"Total: {total_subnets:,G} subnets"

        # If there's an overflow message, combine table with message
        if overflow_message:
            overflow_text = Text(overflow_message, style="dim yellow")
            panel_content = Group(table, overflow_text)
        else:
            panel_content = table

        panel = Panel(
            panel_content,
            title=panel_title,
            title_align="left",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def _add_subnet_row(
        self, subnet: ipaddress.IPv4Network | ipaddress.IPv6Network, table: Table
    ) -> None:
        """Add a subnet row to the table."""
        if subnet.num_addresses == 1:
            # /32 and /128
            table.add_row(
                str(subnet),
                "1",
                str(subnet[0]),
            )
        elif subnet.num_addresses == 2:
            # /31 and /127
            table.add_row(
                str(subnet),
                "2",
                f"{subnet[0]} to {subnet[1]}",
            )
        else:
            table.add_row(
                str(subnet),
                f"{subnet.num_addresses - 2:,G}",
                f"{subnet.network_address + 1} to {subnet.broadcast_address - 1}",
            )

    def split_subnet_by_prefix(
        self,
        network: ipaddress.IPv4Network | ipaddress.IPv6Network,
        new_prefix_len: int,
    ) -> None:
        """Split subnet by specifying new prefix length."""
        try:
            total_subnets = self._calculate_split_count(
                network.prefixlen, new_prefix_len
            )
            table = self._create_subnet_table(total_subnets)
            overflow_message = None

            for i, subnet in enumerate(network.subnets(new_prefix=new_prefix_len)):
                if i >= MAX_DISPLAYED_SUBNETS:
                    overflow_message = (
                        f"... Only showing first {MAX_DISPLAYED_SUBNETS} subnets ..."
                    )
                    break
                self._add_subnet_row(subnet, table)

            self._display_subnet_table_in_panel(table, total_subnets, overflow_message)

        except ValueError as e:
            error_handler.print_error(
                type(e).__name__,
                str(e),
                f"For IPv{network.version}, use a prefix length greater than {network.prefixlen} and less than {128 if network.version == 6 else 32}",
            )

            raise typer.Exit(1)

    def split_subnet_by_count(
        self, network: ipaddress.IPv4Network | ipaddress.IPv6Network, split_count: int
    ) -> None:
        """Split subnet into specified number of parts."""
        try:
            # Finding the x to add to the original mask length
            # Example:
            # split a /24:
            # in 2 parts: /25 -> x = 1 bit longer  -> 2**1 = 2
            # in 4 parts: /26 -> x = 2 bits longer -> 2**2 = 4
            # in 8 parts: /27 -> x = 3 bits longer -> 2**3 = 8
            # in 16 parts: /28
            # ...
            # Calculating the base 2 logarithm of split_num, so that 2**x = split_num
            # Result is rounded up for cases where split_num is not a power of 2.
            prefix_diff = math.ceil(math.log(split_count, 2))
            total_subnets = self._calculate_split_count(
                network.prefixlen, network.prefixlen + prefix_diff
            )
            table = self._create_subnet_table(total_subnets)
            overflow_message = None

            for i, subnet in enumerate(network.subnets(prefixlen_diff=prefix_diff)):
                if i >= MAX_DISPLAYED_SUBNETS:
                    overflow_message = (
                        f"... Only showing first {MAX_DISPLAYED_SUBNETS} subnets ..."
                    )
                    break
                self._add_subnet_row(subnet, table)

            self._display_subnet_table_in_panel(table, total_subnets, overflow_message)

        except (ValueError, ArithmeticError) as e:
            error_handler.print_error(
                type(e).__name__,
                str(e),
                f"Why do you try to split in {split_count}?",
            )
            raise typer.Exit(1)

    def _calculate_split_count(self, original_prefix: int, new_prefix: int) -> int:
        """Calculate number of subnets created by splitting."""
        if new_prefix <= original_prefix:
            raise ValueError("New prefix length must be longer than original length")
        return 2 ** (new_prefix - original_prefix)


########################################################################################################
#                                                                                                      #
# Create the main Typer app                                                                            #
#                                                                                                      #
########################################################################################################

app = typer.Typer(
    help="IPv4 and IPv6 subnet calculator",
    rich_markup_mode="rich",
)


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
    """
    IPv4 and IPv6 subnet calculator.

    Use subcommands to perform specific operations on IP networks.
    """
    if ctx.invoked_subcommand is None:
        # No subcommand was invoked, show informational message
        console = Console()

        console.print()  # Add spacing

        # Create main informational message
        info_text = Text()
        info_text.append("Available commands:\n", style="bold yellow")
        info_text.append("• ", style="dim")
        info_text.append("info", style="bold green")
        info_text.append(
            "     - Display comprehensive network information\n", style="white"
        )
        info_text.append("• ", style="dim")
        info_text.append("split", style="bold green")
        info_text.append("    - Split networks into smaller subnets\n", style="white")
        info_text.append("• ", style="dim")
        info_text.append("examples", style="bold green")
        info_text.append(" - Show usage examples\n\n", style="white")
        info_text.append("Use ", style="dim")
        info_text.append("--help", style="bold cyan")
        info_text.append(" with any command for detailed information.", style="dim")

        # Create panel with the informational message
        panel = Panel(
            info_text,
            title="IPv4 and IPv6 Subnet Calculator",
            title_align="left",
            border_style="bright_blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        console.print(panel)

        # Display Python environment information
        python_panel = create_python_info_panel(console)
        console.print(python_panel)


def create_python_info_panel(console: Console) -> Panel:
    """
    Create a Rich panel displaying Python version and execution environment information.

    Args:
        console: Rich console instance for styling

    Returns:
        Panel: Formatted panel with Python information
    """
    env_info = get_execution_environment()

    # Create info table
    info_table = Table.grid(padding=(0, 2))
    info_table.add_column(style="bold cyan", no_wrap=True)
    info_table.add_column(style="white")

    # Python version and implementation
    info_table.add_row("Python:", f"[bold yellow]{env_info['python_version']}[/]")
    info_table.add_row("Implementation:", f"[dim]{sys.implementation.name}[/]")

    # Environment information
    if env_info["in_virtual_env"]:
        env_style = "green" if env_info["environment_type"] == "uv" else "blue"
        info_table.add_row(
            "Environment:", f"[bold {env_style}]{env_info['environment_type']}[/]"
        )
        if env_info["environment_path"]:
            info_table.add_row(
                "Environment Path:", f"[dim]{env_info['environment_path']}[/]"
            )
    else:
        info_table.add_row("Environment:", "[dim]system (no virtual environment)[/]")

    # Create panel
    panel = Panel(
        info_table,
        title="Python Environment",
        title_align="left",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    return panel


def show_examples():
    """Display examples in a properly formatted Rich panel."""
    console = Console()

    # Get the current script name dynamically
    script_name = os.path.basename(sys.argv[0])

    # Create examples table
    examples_table = Table.grid(padding=(0, 1))
    examples_table.add_column(style="dim", no_wrap=True)  # Description
    examples_table.add_column()  # Command

    # Info examples
    examples_table.add_row("", "[bold cyan]Display subnet information:[/bold cyan]")
    examples_table.add_row(
        "→", f"[green]{script_name} info[/green] [yellow]172.16.0.1/21[/yellow]"
    )
    examples_table.add_row(
        "→",
        f"[green]{script_name} info[/green] [yellow]172.16.0.1[/yellow] [cyan]21[/cyan]",
    )
    examples_table.add_row(
        "→",
        f"[green]{script_name} info[/green] [yellow]10.1.2.0/255.255.255.0[/yellow]",
    )
    examples_table.add_row(
        "→",
        f"[green]{script_name} info[/green] [yellow]10.1.2.0[/yellow] [cyan]255.255.255.0[/cyan]",
    )
    examples_table.add_row(
        "→", f"[green]{script_name} info[/green] [yellow]2001:1:2:3::0/64[/yellow]"
    )
    examples_table.add_row(
        "→",
        f"[green]{script_name} info[/green] [yellow]2001:1:2:3::0[/yellow] [cyan]64[/cyan]",
    )
    examples_table.add_row("", "")  # Empty row
    examples_table.add_row("", "[bold cyan]Split subnets:[/bold cyan]")
    examples_table.add_row(
        "→",
        f"[green]{script_name} split[/green] [yellow]2001:1:2:3::0/64[/yellow] [magenta]--mask[/magenta] [cyan]68[/cyan]",
    )
    examples_table.add_row(
        "→",
        f"[green]{script_name} split[/green] [yellow]192.168.1.0/24[/yellow] [magenta]--count[/magenta] [cyan]8[/cyan]",
    )

    # Create panel with examples
    panel = Panel(
        examples_table,
        title="Examples",
        title_align="left",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    console.print(panel)


def parse_network_input(
    prefix: str, mask: Optional[str] = None
) -> ipaddress.IPv4Network | ipaddress.IPv6Network:
    """Parse network input from command line arguments.
    Args:
        prefix: The IP prefix or address
        mask: Optional subnet mask
    Returns:
        An ipaddress.IPv4Network or ipaddress.IPv6Network object
    """
    try:
        if mask is None:
            prefix_interface = ipaddress.ip_interface(prefix)
        else:
            prefix_string = f"{prefix}/{mask}"
            prefix_interface = ipaddress.ip_interface(prefix_string)

        return prefix_interface.network
    except ValueError as e:
        error_handler.print_error(
            type(e).__name__,
            str(e),
            "Please provide a valid IPv4 or IPv6 network address (e.g., '192.168.1.0/24' or '2001:db8::/32')",
        )
        raise typer.Exit(1)


@app.command()
def examples() -> None:
    """
    Show usage examples for all commands.

    Display comprehensive examples showing how to use the info and split commands
    with various IPv4 and IPv6 network formats.
    """
    show_examples()


@app.command()
def info(
    prefix: Annotated[
        str, typer.Argument(help="The IPv4 or IPv6 prefix, or prefix/mask")
    ],
    mask: Annotated[
        Optional[str], typer.Argument(help="Optional: the subnet mask")
    ] = None,
) -> None:
    """
    Display comprehensive subnet information for IPv4 and IPv6 networks.

    Show network details including version, addresses, netmask, hostmask,
    network/broadcast addresses, host range, and network flags.
    """
    network = parse_network_input(prefix, mask)
    calculator = SubnetCalculator()
    calculator.display_subnet_info(network)


@app.command()
def split(
    prefix: Annotated[
        str, typer.Argument(help="The IPv4 or IPv6 prefix, or prefix/mask")
    ],
    network_mask: Annotated[
        Optional[str], typer.Argument(help="Optional: the subnet mask")
    ] = None,
    count: Annotated[
        Optional[int],
        typer.Option("--count", "-c", help="Number of parts to split the prefix into"),
    ] = None,
    mask: Annotated[
        Optional[int],
        typer.Option(
            "--mask", "-m", help="Length of the subnets to split the prefix into"
        ),
    ] = None,
) -> None:
    """
    Split a subnet into smaller subnets.

    Split the given network into smaller subnets either by specifying:
    - --count: Number of subnets to create
    - --mask: Target prefix length for the subnets

    Only one of --count or --mask can be specified.
    """
    # Ensure exactly one splitting option is provided
    if count is not None and mask is not None:
        error_handler.print_error(
            "Invalid Command Usage",
            "Cannot specify both --count and --mask options",
            "Use either --count to specify number of subnets OR --mask to specify target prefix length",
        )
        raise typer.Exit(1)

    if count is None and mask is None:
        error_handler.print_error(
            "Missing Required Option",
            "Must specify either --count or --mask option",
            "Use --count <number> to split into N subnets OR --mask <length> to create subnets of specific size",
        )
        raise typer.Exit(1)

    network = parse_network_input(prefix, network_mask)
    calculator = SubnetCalculator()

    if mask is not None:
        calculator.split_subnet_by_prefix(network, mask)
    elif count is not None:
        calculator.split_subnet_by_count(network, count)


def main() -> None:
    """Main entry point for the subnet calculator."""
    app()


if __name__ == "__main__":
    main()
