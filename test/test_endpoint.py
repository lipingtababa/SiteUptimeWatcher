#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import os
import sys
from pathlib import Path
import pytest
import re

# To import the src code, we need to add the src directory to the path
src_directory = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(src_directory))
from endpoint import Endpoint

def test_endpoint_with_valid_regex():
    """Test that Endpoint creation works with a valid regex"""
    endpoint = Endpoint(1, "http://example.com", r"Hello\s+World", 60)
    assert endpoint.regex.pattern == r"Hello\s+World"

def test_endpoint_with_invalid_regex():
    """Test that Endpoint creation raises re.error with an invalid regex"""
    with pytest.raises(re.error):
        Endpoint(1, "http://example.com", "(", 60)  # Unmatched parenthesis

def test_endpoint_with_no_regex():
    """Test that Endpoint creation works without a regex"""
    endpoint = Endpoint(1, "http://example.com", None, 60)
    assert not hasattr(endpoint, 'regex')

def test_endpoint_with_empty_regex():
    """Test that Endpoint creation works with an empty regex string"""
    endpoint = Endpoint(1, "http://example.com", "", 60)
    assert not hasattr(endpoint, 'regex') 