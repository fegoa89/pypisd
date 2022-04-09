
import sys, os
import csv
import argparse
import pytest
from unittest import mock
from pypisd.main import cli

@pytest.fixture(autouse=True)
def mock_pypi_request_fetch_page():
    library_html_page_response = open('tests/mock_pypi_library_page_response.html', 'r', encoding='utf-8').read()
    mock_get_request = mock.Mock(side_effect = lambda k:{}.get(k, mock.Mock(text=library_html_page_response)))
    with mock.patch('pypisd.main.requests.get', mock_get_request) as mocked:
        yield mocked


@pytest.fixture()
def requirements_input_file():
    requirements_file_path = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/tests/test_requirements_file.txt"
    with mock.patch('pypisd.main.argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(input_file=requirements_file_path, output_file='pypi_sd_links_from_file.csv')):
        yield mock


def test_pypisd_file_output_header_generation(requirements_input_file):
    cli()
    with open('pypi_sd_links_from_file.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        assert reader.fieldnames == ["library_name", "version", "license", "source_distribution_link"]