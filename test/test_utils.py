#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import os
import sys
from pathlib import Path
import pytest

# To import the src code, we need to add the src directory to the path
src_directory = Path(__file__).resolve().parent.parent / "src"
sys.path.append(str(src_directory))
from utils import load_config_from_file
from detector_exception import EnvException

@pytest.fixture(autouse=True)
def clear_db_env_vars_fixture():
    clear_db_env_vars()

def clear_db_env_vars():
    paras = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    for para in paras:
        os.environ.pop(para, None)

def test_load_config_from_file():
    load_config_from_file(file = "./test/test_data/env_files/.env.valid")
    assert os.getenv("DB_HOST") == "pg-placeholder.a.aivencloud.com"
    assert os.getenv("DB_PORT") == "22047"
    assert os.getenv("DB_NAME") == "MYDB"
    assert os.getenv("DB_USER") == "avnadmin"

def test_load_config_from_file_invalid_port():
    with pytest.raises(EnvException):
        load_config_from_file(file = "./test/test_data/env_files/.env.invalid.port")

def test_load_config_from_file_missing_variable():
    for file in os.listdir("./test/test_data/env_files"):
        if file.startswith(".env.invalid.missing"):
            print("Testing file: " + file)
            # this fixure is invoked manually
            clear_db_env_vars()
            # assert that the exception is raised and msg is correct
            with pytest.raises(EnvException) as e:
                load_config_from_file(file = "./test/test_data/env_files/" + file)
            assert str(e.value) == "DB_HOST, DB_PORT, DB_USER, DB_NAME must be set in the file"
