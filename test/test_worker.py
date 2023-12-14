#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, too-few-public-methods

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

# To import the src code, we need to add the src directory to the path
src_directory = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(src_directory))
from worker import Worker
from endpoint import Endpoint
import utils

@pytest.fixture(autouse=True)
def reset_globals():
    # If not reset, the RUNNING_STATUS will be False after one test and following tests will fail
    utils.RUNNING_STATUS = True

def create_mocked_sleep():
    # Use a closure to avoid global variable
    num_of_monitor_iterations = 0
    # pylint: disable=unused-argument
    async def mocked_sleep(interval):
        nonlocal num_of_monitor_iterations
        num_of_monitor_iterations += 1
        if num_of_monitor_iterations > 1:
            utils.RUNNING_STATUS = False
    return mocked_sleep


@pytest.mark.asyncio
@patch('aiohttp.ClientSession')
@patch('asyncio.sleep', side_effect=create_mocked_sleep())
@patch('metrics.Stat')
@patch('asyncio.Queue', return_value=MagicMock(put=AsyncMock()))
async def test_monitor_with_failed_request(mock_queue, mock_stat, mock_sleep, mock_client_session):
    # here we mock a failed get request
    mock_session_instance = MagicMock(get=AsyncMock(side_effect=Exception("TCP Connection exception")))
    # __aenter__ is a magic method for with statement
    mock_client_session.return_value.__aenter__.return_value = mock_session_instance

    # mock the Stat objects used in the function under test
    mocked_stat_object = mock_stat.return_value
    mocked_stat_object.build_from_successful_http_req = AsyncMock()
    mocked_stat_object.build_from_failed_http_req = MagicMock()

    endpoint = Endpoint(1, "http://testserver:8000", r'.*', 5)
    worker = Worker()
    await worker.monitor(endpoint)

    assert mock_queue.return_value.put.call_count == 2
    mock_queue.return_value.put.assert_called_with(mocked_stat_object)

    assert mocked_stat_object.build_from_successful_http_req.call_count == 0
    assert mocked_stat_object.build_from_failed_http_req.call_count == 2

    mock_sleep.assert_called_with(endpoint.interval)
    assert mock_sleep.call_count == 2
    assert utils.RUNNING_STATUS is False

@pytest.mark.asyncio
@patch('aiohttp.ClientSession')
@patch('asyncio.sleep', side_effect=create_mocked_sleep())
@patch('metrics.Stat')
@patch('asyncio.Queue', return_value=MagicMock(put = AsyncMock()))
async def test_monitor_with_successful_request(mock_queue, mock_stat, mock_sleep, mock_client_session):
    # here we mock a successful get request
    mock_session_instance = MagicMock(get = AsyncMock())
    # __aenter__ is a magic method for with statement
    mock_client_session.return_value.__aenter__.return_value = mock_session_instance

    # mock the Stat objects used in the function under test
    mocked_stat_object = mock_stat.return_value
    mocked_stat_object.build_from_successful_http_req = AsyncMock()
    mocked_stat_object.build_from_failed_http_req = MagicMock()

    endpoint = Endpoint(1, "http://testserver:8000", r'.*', 5)
    worker = Worker()
    await worker.monitor(endpoint)

    assert mock_queue.return_value.put.call_count == 2
    mock_queue.return_value.put.assert_called_with(mocked_stat_object)

    mocked_stat_object.build_from_successful_http_req.assert_called_with(mock_session_instance.get.return_value)
    assert mocked_stat_object.build_from_successful_http_req.call_count == 2
    assert mocked_stat_object.build_from_failed_http_req.call_count == 0

    mock_sleep.assert_called_with(endpoint.interval)
    assert mock_sleep.call_count == 2
    assert utils.RUNNING_STATUS is False
