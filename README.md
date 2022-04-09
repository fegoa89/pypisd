# PyPiSD (PyPi Source Distribution)

CLI tool to fetch source distribution url links from https://pypi.org for a given python package and its version.


## How to use it

### Fetching source distribution url's from environment

Running `pypisd` in your command line, the tool will fetch the packages installed in the environment where the command works. In the background, it fetches this list by runing `pip list`.


### Output of the CLI task

After running `pypisd` the output will be saved in a csv file. By default, the file name is "pypi_sd_links.csv".
You can providen the file name where the output should be saved by running:

```
$ pypisd --output_file="my_file_csv"
```

```
$ pypisd --o="my_file_csv"
```


The file has the following columns:

- library_name: Name of the library.
- version: version of the library. If none could be read from the environment/input file, "using latest version" will be used instead.
- license: Defines the license that the library uses
- source_distribution_link: Link to download the source distribution for this given library&version. If not found, it will be replaced by "Can not find download link for My Library, version 0.0.1"