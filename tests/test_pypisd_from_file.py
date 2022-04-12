
import os
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
    requirements_file_path = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/tests/test_input_file.txt"
    with mock.patch('pypisd.main.argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(input_file=requirements_file_path, output_file='pypi_sd_links_from_file.csv')):
        yield mock

@pytest.fixture()
def wrong_path_input_file():
    requirements_file_path = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/tests/something_wrong.txt"
    with mock.patch('pypisd.main.argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(input_file=requirements_file_path, output_file='pypi_sd_links_from_file.csv')):
        yield mock

@pytest.fixture()
def toml_input_file():
    toml_file_path = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/tests/pyproject_test.toml"
    with mock.patch('pypisd.main.argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(input_file=toml_file_path, output_file='pypi_sd_links_from_file.csv')):
        yield mock

def test_pypisd_file_output_header_generation(requirements_input_file):
    cli()
    with open('pypi_sd_links_from_file.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        assert reader.fieldnames == ["library_name", "version", "license", "source_distribution_link"]


def test_pypisd_file_test_library_row_content(requirements_input_file):
    cli()
    with open('pypi_sd_links_from_file.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        reader_list = list(reader)
        # license and source_distribution_link are the same since we
        # are mocking the requests
        reader_list = sorted(reader_list, key = lambda i: i['library_name'])

        assert reader_list[0]["library_name"] == "Click"
        assert reader_list[0]["version"] == "7.0"
        assert reader_list[1]["library_name"] == "Flask"
        assert reader_list[1]["version"] == "using latest version"
        assert reader_list[2]["library_name"] == "beautifulsoup4"
        assert reader_list[2]["version"] == "4.6.3"
        assert reader_list[3]["library_name"] == "bleach"
        assert reader_list[3]["version"] == "2.1.4"
        assert reader_list[4]["library_name"] == "certifi"
        assert reader_list[4]["version"] == "2018.8.24"
        assert reader_list[5]["library_name"] == "chardet"
        assert reader_list[5]["version"] == "3.0.4"
        assert reader_list[6]["library_name"] == "cycler"
        assert reader_list[6]["version"] == "0.10.0"
        assert reader_list[7]["library_name"] == "decorator"
        assert reader_list[7]["version"] == "4.3.0"
        assert reader_list[8]["library_name"] == "defusedxml"
        assert reader_list[8]["version"] == "0.5.0"
        assert reader_list[9]["library_name"] == "requests"
        assert reader_list[9]["version"] == "2.27.1"


def test_pypisd_toml_file_input(toml_input_file):
    cli()
    with open('pypi_sd_links_from_file.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        reader_list = list(reader)
        # license and source_distribution_link are the same since we
        # are mocking the requests
        reader_list = sorted(reader_list, key = lambda i: i['library_name'])
        assert reader_list[0]["library_name"] == "bs4"
        assert reader_list[0]["version"] == "0.0.1"
        assert reader_list[1]["library_name"] == "requests"
        assert reader_list[1]["version"] == "2.27.1"
        assert reader_list[2]["library_name"] == "toml"
        assert reader_list[2]["version"] == "0.10.2"

def test_pypisd_with_wrong_file_input(wrong_path_input_file):
    with pytest.raises(SystemExit) as e:
        cli()

    assert e.type == SystemExit
    assert e.value.code == 1
