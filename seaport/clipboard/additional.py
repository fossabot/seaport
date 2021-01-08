"""Additional checks that aren't provided by default.

e.g. Linting
"""

import subprocess

import click

from seaport.clipboard.checks import user_path
from seaport.clipboard.format import format_subprocess


def perform_lint(name: str) -> bool:
    """Lints the port and checks output for errors.

    Args:
        name: The name of the port

    Returns:
        bool: Whether the linting was successful or not
    """
    click.secho("🤔 Linting", fg="cyan")
    lint_output = format_subprocess(
        [f"{user_path(True)}/port", "lint", "--nitpick", name]
    )
    click.echo(lint_output)
    output_list = lint_output.split(" ")

    # Finds the no. of errors and warnings
    errors = int(output_list[output_list.index("errors") - 1])
    warnings = int(output_list[output_list.index("warnings") - 1])

    if errors > 1:
        # Fail if there are any errors
        return False
    if warnings > 1:
        # Ask whether the user wishes to continue
        if not click.confirm(
            f"There are {warnings} warnings. Do you wish to continue?"
        ):
            return False
    return True


def perform_test(name: str, subport: str) -> bool:
    """Tests the port and checks output for errors.

    Args:
        name: The name of the port
        subport: The name of one of the subports

    Returns:
        bool: Whether the tet was successful or not
    """
    click.secho(f"🧪 Testing {name}", fg="cyan")
    try:
        subprocess.run(
            [f"{user_path()}/sudo", f"{user_path(True)}/port", "test", name],
            check=True,
        )
    except subprocess.CalledProcessError:
        # For python ports, the tests are in the subport
        # There are no tests in the original port
        if subport:
            click.secho(f"🏗 Trying with subport {subport}", fg="cyan")
            try:
                subprocess.run(
                    [f"{user_path()}/sudo", f"{user_path(True)}/port", "test", subport],
                    check=True,
                )
            except subprocess.CalledProcessError:
                click.secho("❌ Tests failed", fg="red")
                return False
        else:
            click.secho("❌ Tests failed", fg="red")
            return False
    click.secho("✅ Tests passed", fg="green")
    return True