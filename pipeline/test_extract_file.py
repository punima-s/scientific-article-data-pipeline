from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock
from extract_file import get_objects, get_latest_file, downloading_files, extract_main


def test_get_objects():
    fake_client = MagicMock()
    fake_client.list_objects.return_value = {"Contents":
                                             [{"Key": "c11-punima/fake_file",
                                              "Size": 3,
                                               "LastModified": "Fake Date"},
                                              {"Key": "c11-punima/fake_file",
                                              "Size": 0,
                                               "LastModified": "Fake Date"},
                                              {"Key": "c11-/fake_file",
                                              "Size": 3,
                                               "LastModified": "Fake Date"}]
                                             }
    result = get_objects(fake_client, "fake_bucket")
    assert result == [('c11-punima/fake_file', 'Fake Date')]


def test_get_latest_file():
    # datetime(year, month, day, hour, minute, second, microsecond)
    earliest = datetime(2022, 12, 28, 23, 55, 59, 342380)
    middle = datetime(2023, 12, 28, 23, 55, 59, 342380)
    latest = datetime(2024, 4, 28, 23, 55, 59, 342380)
    fake_objects = [("fake_file_1", earliest),
                    ("fake_file_2", middle), ("fake_file_3", latest)]
    assert get_latest_file(fake_objects) == ("fake_file_3", latest)


@patch('extract_file.environ')
def test_get_latest_file_empty(fake_environ):
    fake_client = MagicMock()
    fake_environ['INPUT_BUCKET'].return_value = 'fake_bucket'
    with pytest.raises(ValueError):
        downloading_files(
            fake_client, fake_environ['INPUT_BUCKET'], [])


@patch('extract_file.get_objects')
@patch('extract_file.environ')
def test_get_latest_file_empty(fake_environ, fake_get_objects):
    fake_get_objects.return_value = []
    fake_environ['INPUT_BUCKET'].return_value = 'fake_bucket'
    assert extract_main() == {"Error: No files in this bucket!"}
