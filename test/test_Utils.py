#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import os
import sys
from pathlib import Path

# To import the src code, we need to add the src directory to the path
src_directory = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(src_directory))
from utils import loadConfigFromFile
from detector_expections import EnvException

@pytest.fixture(autouse=True)
def clear_db_env_vars_fixture():
    clear_db_env_vars()

def clear_db_env_vars():
    vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    for var in vars:
        os.environ.pop(var, None)

def test_loadConfigFromFile():
    loadConfigFromFile(file = "./test/test_data/env_files/.env.valid")
    assert os.getenv("DB_HOST") == "pg-placeholder.a.aivencloud.com"
    assert os.getenv("DB_PORT") == "22047"
    assert os.getenv("DB_NAME") == "MYDB"
    assert os.getenv("DB_USER") == "avnadmin"
    assert os.getenv("DB_PASSWORD") == "AVNS_1234567890"

def test_loadConfigFromFile_invalid_port():
    with pytest.raises(EnvException):
        loadConfigFromFile(file = "./test/test_data/env_files/.env.invalid.port")

def test_loadConfigFromFile_missing_variable():
    print("Hello")
    for file in os.listdir("./test/test_data/env_files"):
        if file.startswith(".env.invalid.missing"):
            print("Testing file: " + file)
            # this fixture must be called before every test
            clear_db_env_vars()
            # assert that the exception is raised and msg is correct
            with pytest.raises(EnvException) as e:
                loadConfigFromFile(file = "./test/test_data/env_files/" + file)
            assert str(e.value) == "DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME must be set"
