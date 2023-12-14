#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, too-few-public-methods

import sys
import time
from pathlib import Path
import pytest

# To import the src code, we need to add the src directory to the path
src_directory = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(src_directory))
from metrics import Stat
from endpoint import Endpoint

class aiohttp_response:
    def __init__(self, status=200, resp_data=None):
        self.status = status
        self.resp_data = resp_data

    async def text(self):
        return self.resp_data


@pytest.mark.asyncio
async def test_build_from_successful_http_req_match_with_simple_regex():
    endpoint_with_simple_regex = Endpoint(1, "http://testserver:8000", ".*welcome", 5)
    stat = Stat(endpoint_with_simple_regex, time.time()-1)
    resp = aiohttp_response(200, "You are always welcome!")

    await stat.build_from_successful_http_req(resp)
    assert stat.duration > 0
    assert stat.status_code == 200
    assert stat.regex_match is True

endpoint = Endpoint(1, "http://testserver:8000", r"you.*welcome at\s[0-9]{2}:[0-9]{2}$", 5)

@pytest.mark.asyncio
async def test_build_from_successful_http_req_match():
    stat = Stat(endpoint, time.time()-1)
    resp = aiohttp_response(200, "you are welcome at 12:00")

    await stat.build_from_successful_http_req(resp)
    assert stat.duration > 0
    assert stat.status_code == 200
    assert stat.regex_match is True

@pytest.mark.asyncio
async def test_build_from_successful_http_req_not_match():
    stat = Stat(endpoint, time.time()-1)
    resp = aiohttp_response(200, "Hello World")

    await stat.build_from_successful_http_req(resp)
    assert stat.duration > 0
    assert stat.status_code == 200
    assert stat.regex_match is False

@pytest.mark.asyncio
async def test_build_from_successful_http_req_200():
    stat = Stat(endpoint, time.time()-1)
    resp = aiohttp_response(500, "you are welcome at 12:00")

    await stat.build_from_successful_http_req(resp)
    assert stat.duration > 0
    assert stat.status_code == 500
    assert stat.regex_match is False

def test_build_from_failed_http_req():
    stat = Stat(endpoint, time.time()-1)
    stat.build_from_failed_http_req()
    assert stat.duration > 0
    assert stat.status_code == 0
    assert stat.regex_match is False
