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
