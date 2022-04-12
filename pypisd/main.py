import sys
import os
import re
import csv
import toml
import argparse
import requests
import pathlib
from subprocess import Popen, PIPE, STDOUT
import concurrent.futures
from bs4 import BeautifulSoup


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_file",
        help="File use to read libraries from instead of the environment",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="File where the source distribution links will be saved, default 'pypi_sd_links.csv'",
    )
    args = parser.parse_args()
    if args.input_file:
        # Get libraries from file
        lib_list = fetch_libraries_from_file(args.input_file)
    else:
        # Get libraries from environment
        lib_list = fetch_libraries_from_environment()

    # Fetch source distribution download link for each library & version
    source_distribution_list = fetch__and_extract_details_for_library_list(lib_list)
    # Write source distribution list to CSV
    write_library_info_to_csv(source_distribution_list, args.output_file)


def fetch_libraries_from_environment() -> list(list()):
    lib_list_bytes = get_pip_list_stdout()
    return extract_lib_list_from_bytes_output(lib_list_bytes)


def fetch_libraries_from_file(file_path: str) -> list(list()):
    if not os.path.isfile(file_path):
        print(f"Input file {file_path} do not exist")
        sys.exit(1)

    file_suffix = pathlib.Path(file_path).suffix
    if file_suffix == ".toml":
        return fetch_lib_list_from_toml_file(file_path)
    else:
        with open(file_path) as f:
            lines = f.readlines()
            return [
                re.split("[<|>|~=|==|!=|<=|>=|===|, \!?:]+", line.strip())
                for line in lines
            ]


def fetch_lib_list_from_toml_file(file_path: str) -> list(list()):
    data = toml.load(file_path)
    dependencies = data["tool"]["poetry"]["dependencies"]
    lib_list = []
    for key, val in dependencies.items():
        lib_list.append([key, re.sub(r"[(\^\s*)|(\~\s*)]", "", val)])

    return lib_list


def fetch__and_extract_details_for_library_list(lib_list: list) -> list(list()):
    source_distribution_list = list()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for library in lib_list:
            version = library[1] if len(library) == 2 else None
            futures.append(
                executor.submit(
                    get_source_distribution_link_for_library,
                    library=library[0],
                    version=version,
                )
            )
        for future in concurrent.futures.as_completed(futures):
            source_distribution_list.append(future.result())

    return source_distribution_list


def get_pip_list_stdout() -> bytes:
    pip_freeze_process = Popen(["pip", "list"], stdout=PIPE, stderr=STDOUT)
    print(pip_freeze_process.communicate())
    output, error = pip_freeze_process.communicate()
    if error:
        print(f"Error while getting list of libraries from environment {error}")
        sys.exit(1)

    return output


def extract_lib_list_from_bytes_output(pip_stdout: bytes) -> list:
    lib_list = list()
    for output_line in pip_stdout.splitlines()[2:]:
        line = output_line.decode("utf-8").split()
        if len(line) == 2:
            lib_list.append(line)

    return lib_list


def get_source_distribution_link_for_library(
    library: str, version: str, timeout=10
) -> list:
    if version:
        url = f"https://pypi.org/project/{library}/{version}/#files"
    else:
        url = f"https://pypi.org/project/{library}/#files"

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    library_license = soup.find("strong", text="License:")
    library_license = (
        library_license.next_sibling.strip() if library_license else "Not found"
    )
    get_download_link_div = soup.find("div", {"class": "card file__card"})

    if get_download_link_div:
        source_download_link = soup.find("div", {"class": "card file__card"}).find("a")[
            "href"
        ]
        return [
            library,
            version if version else "using latest version",
            library_license,
            source_download_link,
        ]
    else:
        return [
            library,
            version if version else "using latest version",
            library_license,
            f"Can not find download link for {library}, version {version}",
        ]


def write_library_info_to_csv(sd_list: list(list()), file_name: str):
    file_name = file_name if file_name else "pypi_sd_links.csv"
    with open(file_name, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(
            ["library_name", "version", "license", "source_distribution_link"]
        )
        # write multiple rows
        writer.writerows(sd_list)
        print(f"Results available in {file_name}")
