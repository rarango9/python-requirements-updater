#!/usr/bin/env python3
# ======================================================================
# Updates Python requirements to the latest package versions attempting
# to keep the original delimiter.
# ======================================================================

from argparse import ArgumentParser
from os.path import isfile
from re import split
import re
from sys import exit
from urllib.error import URLError
from urllib.request import Request, urlopen
import json
import pathlib


prefix = '\033[36;1m❱❱\033[0m'


def main():
    # Parses arguments that were passed to the script and validates them
    # using Argparse.
    p = ArgumentParser()
    p.add_argument('file_path')
    p.add_argument('-w', '--write', action='store_true')
    args = p.parse_args()

    print('┌─┐┬ ┬┌┬┐┬ ┬┌─┐┌┐┌  ┬─┐┌─┐┌─┐ ┬ ┬┬┬─┐┌─┐┌┬┐┌─┐┌┐┌┌┬┐┌─┐  ┬ ┬┌─┐┌┬┐┌─┐┌┬┐┌─┐┬─┐',
          '├─┘└┬┘ │ ├─┤│ ││││  ├┬┘├┤ │─┼┐│ ││├┬┘├┤ │││├┤ │││ │ └─┐  │ │├─┘ ││├─┤ │ ├┤ ├┬┘',
          '┴   ┴  ┴ ┴ ┴└─┘┘└┘  ┴└─└─┘└─┘└└─┘┴┴└─└─┘┴ ┴└─┘┘└┘ ┴ └─┘  └─┘┴  ─┴┘┴ ┴ ┴ └─┘┴└─',
          sep='\n', end='\n\n')

    # Get the absolute path to the requirements file.
    abs_path = pathlib.Path(args.file_path).resolve()

    # Attempt to load the file and print error is not found.
    try:
        with open(abs_path, 'r') as f:
            old_contents = sorted(f.read().splitlines())
            print(prefix, 'Old Contents:')
            print('\n'.join(old_contents), end='\n\n')
    except FileNotFoundError as e:
        print(e)
        exit(1)

    # Loop through the old contents.
    new_contents = []
    for line in sorted(old_contents):

        # Add any external file loads to without changes to the new content.
        if line.startswith('-r '):
            new_contents.append(line)

        # Parse each dependency and check for any new versions.
        else:
            package, version = split(r'[=<>!~]+', line)
            delimiter = line.replace(package, '').replace(version, '')

            try:
                request = Request(F"https://pypi.org/pypi/{package}/json")
                response = urlopen(request).read()
                latest_version = json.loads(response)['info']['version']
                new_contents.append(F"{package}{delimiter}{latest_version}")
            except URLError as e:
                print(F"Failed looking up: {package}")
                new_contents.append(line)

    # Print the new contents out to console.
    print(prefix, 'New Contents:')
    for old_line in old_contents:
        index = old_contents.index(old_line)
        if old_line != new_contents[index]:
            print(F"\033[33;1m{new_contents[index]}\033[0m")
        else:
            print(old_line)
    print()

    # Write the contents out to the file or display a reminder that you can.
    if args.write:
        with open(abs_path, 'w+') as f:
            f.write('\n'.join(sorted(new_contents)))
            print(prefix, 'New requirements written to file')
    else:
        print(prefix, 'Review the changes above (Any changes are in yellow)')
        print("   To write the changes, re-run with '-w' or '--write'")


if __name__ == '__main__':
    main()
