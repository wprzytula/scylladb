#
# Copyright 2023-present ScyllaDB
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import pytest
from rest_api_mock import expected_request
import subprocess

import utils


# These are simple smoke tests, because automatically testing help is next to impossible.


def test_help(nodetool):
    res = nodetool("help", expected_requests=[
        # These requests are sometimes sent by Cassandra nodetool when invoking help
        # This looks like a new connection to JMX.
        expected_request("GET", "/column_family/", response=[], multiple=expected_request.ANY),
        expected_request("GET", "/stream_manager/", response=[], multiple=expected_request.ANY),
    ])
    assert res.stdout


def test_help_command(nodetool):
    res = nodetool("help", "version")
    assert res.stdout


def test_help_nonexistent_command(request, nodetool):
    if request.config.getoption("nodetool") == "scylla":
        utils.check_nodetool_fails_with(
                nodetool,
                ("help", "foo",),
                {},
                ["error processing arguments: unknown command foo"])
    else:
        res = nodetool("help", "foo")
        assert res.stdout == "Unknown command foo\n\n"


def test_help_command_too_many_args(nodetool, scylla_only):
    utils.check_nodetool_fails_with(
            nodetool,
            ("help", "compact", "foo", "bar"),
            {},
            ["error: too many positional options have been specified on the command line"])


def test_help_consistent(nodetool, scylla_only):
    for command in ("version", "compact", "settraceprobability"):
        res1 = nodetool("help", command)
        res2 = nodetool(command, "--help", check_return_code=False)
        # TODO: older seastar returns 1 when --help is invoked
        #       remove the check_return_code parameter above after
        #       updating the seastar submodule
        assert res2.returncode in (1, 0)
        assert res1.stdout == res2.stdout
