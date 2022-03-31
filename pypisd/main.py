import requests
from bs4 import BeautifulSoup
import threading
import subprocess

global_lock = threading.Lock()

def cli():
    lib_list_bytes = get_pip_list_stdout()
    lib_list = extract_lib_list_from_bytes_output(lib_list_bytes)
    threads = []

    for library in lib_list:
        t = threading.Thread(target=get_source_distribution_link_for_library(library))
        threads.append(t)
        t.start()
    [thread.join() for thread in threads]

def get_pip_list_stdout() -> bytes:
    pip_freeze_process = subprocess.Popen(['pip', 'list'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return pip_freeze_process.stdout.read()

def extract_lib_list_from_bytes_output(pip_stdout: bytes) -> list:
    lib_list = list()
    for output_line in pip_stdout.splitlines()[2:]:
        line = output_line.decode("utf-8").split()
        if len(line) == 2:
            lib_list.append(line)

    return lib_list


def get_source_distribution_link_for_library(library: list):
    if len(library) == 2:
        url = f"https://pypi.org/project/{library[0]}/{library[1]}/#files"
    else:
        url = f"https://pypi.org/project/{library[0]}/#files"

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    get_download_link_div = soup.find("div", {"class": "card file__card"})

    with open("thread_writes", "a+") as file:
        if get_download_link_div:
            file.write(f'{library[0]},{library[1] if (len(library) == 2) else "using latest version"},{soup.find("div", {"class": "card file__card"}).find("a")["href"]}\n')
        else:
            file.write(f"Can not find download link for {library[0]}, version {library[1]}\n")