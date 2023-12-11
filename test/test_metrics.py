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

endpoint = Endpoint(1, "http://testserver:8000", r"you.*welcome at\s[0-9]{2}:[0-9]{2}$", 5)

@pytest.mark.asyncio
async def test_initFromHTTPResponse_match():
    stat = Stat(endpoint, time.time()-1)
    resp = aiohttp_response(200, "you are welcome at 12:00")

    await stat.initFromHTTPResponse(resp)
    assert stat.duration > 0
    assert stat.statusCode == 200
    assert stat.regexMatch is True

@pytest.mark.asyncio
async def test_initFromHTTPResponse_not_match():
    stat = Stat(endpoint, time.time()-1)
    resp = aiohttp_response(200, "Hello World")

    await stat.initFromHTTPResponse(resp)
    assert stat.duration > 0
    assert stat.statusCode == 200
    assert stat.regexMatch is False

@pytest.mark.asyncio
async def test_initFromHTTPResponse_not_200():
    stat = Stat(endpoint, time.time()-1)
    resp = aiohttp_response(500, "you are welcome at 12:00")

    await stat.initFromHTTPResponse(resp)
    assert stat.duration > 0
    assert stat.statusCode == 500
    assert stat.regexMatch is False
    