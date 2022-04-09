import os
import csv
import argparse
import pytest
from unittest import mock
from pypisd.main import cli

pip_list_output = b'Package            Version\n------------------ ---------\nrequests           2.27.1\n'

@pytest.fixture(autouse=True)
def mock_pip_list_command():
    with mock.patch('pypisd.main.Popen') as mocked:
        mocked.return_value.returncode = 0
        mocked.return_value.communicate.return_value = (pip_list_output, None)
        yield mocked

@pytest.fixture(autouse=True)
def mock_pypi_request_fetch_page():
    library_html_page_response = open('tests/mock_pypi_library_page_response.html', 'r', encoding='utf-8').read()
    mock_get_request = mock.Mock(side_effect = lambda k:{}.get(k, mock.Mock(text=library_html_page_response)))
    with mock.patch('pypisd.main.requests.get', mock_get_request) as mocked:
        yield mocked

def test_pypisd_file_output_header_generation():
    cli()
    with open('pypi_sd_links.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        assert reader.fieldnames == ["library_name", "version", "license", "source_distribution_link"]

def test_pypisd_file_test_library_row_content():
    cli()
    with open('pypi_sd_links.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        first_row = next(reader)
        assert first_row['library_name'] == 'requests'
        assert first_row['version'] == '2.27.1'
        assert first_row['license'] == 'Apache Software License (Apache 2.0)'
        assert first_row['source_distribution_link'] == 'https://files.pythonhosted.org/packages/60/f3/26ff3767f099b73e0efa138a9998da67890793bfa475d8278f84a30fec77/requests-2.27.1.tar.gz'

def test_pypisd_default_file_output_name():
    cli()
    assert os.path.isfile("pypi_sd_links.csv") == True

@mock.patch('pypisd.main.argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(output_file="myfile.csv"))
def test_pypisd_file_output_name_if_provided_by_input(mock_args):
    cli()
    assert os.path.isfile("myfile.csv") == True
