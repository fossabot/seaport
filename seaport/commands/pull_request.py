#!/usr/bin/env python3

# Copyright (c) 2021, harens
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of seaport nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Command to send a PR after updating portfile."""

import os
import subprocess
from typing import Any

import click

from seaport.clipboard.checks import user_path
from seaport.clipboard.format import format_subprocess
from seaport.commands.autocomplete.autocomplete import get_names
from seaport.commands.clipboard import clip
from seaport.pull_request.portfile import determine_category, new_contents


@click.command()
@click.argument("name", type=str, autocompletion=get_names)
@click.argument(
    "location",
    type=click.Path(exists=True, dir_okay=True, writable=True),
)
# Some versions could be v1.2.0-post for example
@click.option("--bump", help="The new version number", type=str)
@click.option("--test/--no-test", default=False, help="Runs port test")
@click.option("--lint/--no-lint", default=False, help="Runs port lint --nitpick")
@click.option(
    "--install/--no-install",
    default=False,
    help="Installs the port and allows testing of basic functionality",
)
@click.option("--new", is_flag=True, help="Send a PR from the local portfile repo")
@click.pass_context
def pr(
    ctx: Any,
    name: str,
    bump: str,  # bump is used as part of ctx.forward
    location: str,
    test: bool,
    lint: bool,
    install: bool,
    new: bool,
) -> None:
    """Bumps the version number and checksum of NAME, and sends a PR to update it."""
    # Invoke the clipboard cmd
    # That's the command that determines the new contents
    ctx.forward(clip)

    # Retrieve new version number and contents
    contents, bump = new_contents()

    # Assumes first category is where to put the portfile
    category = determine_category(name)

    click.secho("🚀 Cloning macports/macports-ports", fg="cyan")
    os.chdir(location)
    # check false if macports-ports already exists (error 127)
    subprocess.run(
        [
            f"{user_path(False, True)}/gh",
            "repo",
            "fork",
            "macports/macports-ports",
            "--clone=true",
            "--remote=true",
        ],
        check=False,
    )

    # Update origin
    os.chdir(f"{location}/macports-ports")
    subprocess.run([f"{user_path()}/git", "fetch", "upstream"], check=True)
    subprocess.run([f"{user_path()}/git", "merge", "upstream/master"], check=True)
    subprocess.run([f"{user_path()}/git", "push"], check=True)

    # Different titles depending on whether updating
    # or adding new file
    commit_title = f"{name}: new port" if new else f"{name}: update to {bump}"

    subprocess.run(
        [f"{user_path()}/git", "checkout", "-b", f"seaport-{name}-{bump}"],
        check=True,
    )

    # Remove backslash from user macports repo location
    # This allows copyfile to work regardless of whether there's
    # a backslash or not
    location = location.rstrip("/")

    if new:
        # Have to create directories for new portfile
        subprocess.run(
            ["/bin/mkdir", "-p", f"{location}/macports-ports/{category}/{name}"],
            check=True,
        )

    # Add the new contents to the portfile
    with open(f"{location}/macports-ports/{category}/{name}/Portfile", "w") as portfile:
        portfile.write(contents)

    subprocess.run(
        [f"{user_path()}/git", "add", f"{category}/{name}/Portfile"], check=True
    )
    subprocess.run(
        [f"{user_path()}/git", "commit", "-m", commit_title],
        check=True,
    )
    # Automatically choose to send PR to remote
    # Change to remote.origin.gh-resolved to send to user's fork
    subprocess.run(
        [f"{user_path()}/git", "config", "remote.upstream.gh-resolved", "base"],
        check=True,
    )

    # PR variables
    mac_version = format_subprocess([f"{user_path()}/sw_vers", "-productVersion"])
    xcode_version = format_subprocess(
        [f"{user_path()}/xcodebuild", "-version"]
    ).replace("\nBuild version", "")

    if click.confirm("Does everything look good before sending PR?"):
        subprocess.run(
            [
                f"{user_path()}/git",
                "push",
                "--set-upstream",
                "origin",
                f"seaport-{name}-{bump}",
            ],
            check=True,
        )
        subprocess.run(
            [
                f"{user_path(False, True)}/gh",
                "pr",
                "create",
                "--title",
                commit_title,
                "--body",
                f"""#### Description

Created with [seaport](https://github.com/harens/seaport)

###### Type(s)

- [ ] bugfix
- [x] enhancement
- [ ] security fix

###### Tested on
macOS {mac_version}
{xcode_version}

###### Verification <!-- (delete not applicable items) -->
Have you

- [x] followed our [Commit Message Guidelines](https://trac.macports.org/wiki/CommitMessages)?
- [x] squashed and [minimized your commits](https://guide.macports.org/#project.github)?
- [ ] checked that there aren't other open [pull requests](https://github.com/macports/macports-ports/pulls) for the same change?
- [ ] referenced existing tickets on [Trac](https://trac.macports.org/wiki/Tickets) with full URL? <!-- Please don't open a new Trac ticket if you are submitting a pull request. -->
- [{"x" if lint else " "}] checked your Portfile with `port lint`?
- [{"x" if test else " "}] tried existing tests with `sudo port test`?
- [{"x" if install else " "}] tried a full install with `sudo port -vst install`?
- [{"x" if install else " "}] tested basic functionality of all binary files?""",
            ],
            check=True,
        )
    # cleanup process
    subprocess.run([f"{user_path()}/git", "checkout", "master"], check=True)
    subprocess.run(
        [f"{user_path()}/git", "branch", "-D", f"seaport-{name}-{bump}"], check=True
    )
