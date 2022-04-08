import csv
import requests
from subprocess import Popen, PIPE, STDOUT
import concurrent.futures
from bs4 import BeautifulSoup

def cli():
    lib_list_bytes = get_pip_list_stdout()
    lib_list = extract_lib_list_from_bytes_output(lib_list_bytes)
    source_distribution_list = list()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for library in lib_list:
            futures.append(executor.submit(get_source_distribution_link_for_library, library=library[0], version=library[1]))
        for future in concurrent.futures.as_completed(futures):
            source_distribution_list.append(future.result())

    write_library_info_to_csv(source_distribution_list)

def get_pip_list_stdout() -> bytes:
    pip_freeze_process = Popen(['pip', 'list'], stdout=PIPE, stderr=STDOUT)
    output, error = pip_freeze_process.communicate()
    if error:
        print("Error while getting list of libraries from environment")

    return output

def extract_lib_list_from_bytes_output(pip_stdout: bytes) -> list:
    lib_list = list()
    for output_line in pip_stdout.splitlines()[2:]:
        line = output_line.decode("utf-8").split()
        if len(line) == 2:
            lib_list.append(line)

    return lib_list

def get_source_distribution_link_for_library(library, version, timeout=10):
    if version:
        url = f"https://pypi.org/project/{library}/{version}/#files"
    else:
        url = f"https://pypi.org/project/{library}/#files"

    page = requests.get(url)
    print(page.text)
    soup = BeautifulSoup(page.text, 'html.parser')
    library_license = soup.find('strong',text='License:')
    library_license = library_license.next_sibling if library_license else "Not found"
    get_download_link_div = soup.find("div", {"class": "card file__card"})

    if get_download_link_div:
        source_download_link = soup.find("div", {"class": "card file__card"}).find("a")["href"]
        return [library, version if version else "using latest version", library_license, source_download_link]
    else:
        return [library, version if version else "using latest version", library_license, f"Can not find download link for {library}, version {version}"]

def write_library_info_to_csv(sd_list):
    with open('pypi_sd_links.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(['library_name', "version", "license", "source_distribution_link"])
        # write multiple rows
        writer.writerows(sd_list)