#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import os
import sys
from pathlib import Path

# To import the src code, we need to add the src directory to the path
src_directory = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(src_directory))
from Utils import loadConfigFromFile
from Exceptions import EnvException


@pytest.fixture(autouse=True)
def clear_db_env_vars():
    vars_to_clear = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    for var in vars_to_clear:
        os.environ.pop(var, None)

def test_loadConfigFromFile():
    loadConfigFromFile(file = "./test_data/env_files/.env.valid")
    assert os.getenv("DB_HOST") == "pg-placeholder.a.aivencloud.com"
    assert os.getenv("DB_PORT") == "22047"
    assert os.getenv("DB_NAME") == "MYDB"
    assert os.getenv("DB_USER") == "avnadmin"
    assert os.getenv("DB_PASSWORD") == "AVNS_1234567890"

def test_loadConfigFromFile_invalid_port():
    with pytest.raises(EnvException):
        loadConfigFromFile(file = "./test_data/env_files/.env.invalid.invalidport")

def test_loadConfigFromFile_missing_variable():
    for file in os.listdir("./test_data/env_files"):
        if file.startswith(".env.invalid.missing."):
            with pytest.raises(EnvException):
                loadConfigFromFile(file = f"./test_data/envFiles/{file}")
