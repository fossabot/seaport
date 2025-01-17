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

import subprocess

from pytest_mock import MockFixture

from seaport.clipboard.additional import perform_lint, perform_test


def test_perform_lint(fake_process, session_mocker: MockFixture) -> None:

    # If there are errors present in port lint

    # Set default path
    session_mocker.patch(
        "seaport.clipboard.additional.user_path", return_value="/opt/local/bin"
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "lint", "--nitpick", "some-port"],
        stdout=[
            "--->  Verifying Portfile for some-port\n--->  2 errors and 3 warnings found."
        ],
    )

    assert not perform_lint("some-port")

    # If there are warnings and the user chooses to continue

    session_mocker.patch("click.confirm", return_value=True)

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "lint", "--nitpick", "some-port"],
        stdout=[
            "--->  Verifying Portfile for some-port\n--->  0 errors and 3 warnings found."
        ],
        occurrences=2,
    )

    assert perform_lint("some-port")

    # If there are warnings and the user chooses not to continue

    session_mocker.patch("click.confirm", return_value=False)

    assert not perform_lint("some-port")

    # If there are no errors and no warnings

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "lint", "--nitpick", "some-port"],
        stdout=[
            "--->  Verifying Portfile for some-port\n--->  0 errors and 0 warnings found."
        ],
        occurrences=2,
    )

    assert perform_lint("some-port")


def callback_info(process) -> None:
    """`port test name` output if tests fail"""
    raise subprocess.CalledProcessError(1, cmd="port test someport")


def test_perform_test(fake_process, session_mocker: MockFixture) -> None:

    # Set default path
    # Both sudo and port used (hence example)
    session_mocker.patch(
        "seaport.clipboard.additional.user_path", return_value="/example"
    )

    # If the tests pass

    fake_process.register_subprocess(
        ["/example/sudo", "/example/port", "test", "some-port"],
        stdout=["Testing some-port"],
    )

    assert perform_test("some-port", "some-subport")

    # If all tests fail

    # Tests for main port
    fake_process.register_subprocess(
        ["/example/sudo", "/example/port", "test", "some-port"],
        callback=callback_info,
        occurrences=2,
    )

    # Tests for subport
    fake_process.register_subprocess(
        ["/example/sudo", "/example/port", "test", "some-subport"],
        callback=callback_info,
    )

    assert not perform_test("some-port", "some-subport")

    # IF there's no subports

    assert not perform_test("some-port", "")
