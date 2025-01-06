#!/usr/bin/env python3
# Read a setlist and report how long the entire performance will be

import argparse
import sys
from collections import namedtuple
import os
import re

def parseArgs():
    parser = argparse.ArgumentParser(description='Report total duration of songs in a set list')

    parser.add_argument('setlist',
                        help='The setlist file.')

    args = parser.parse_args()
    return args

def main():
    duration_prog = re.compile(r'\{duration:\s*(\d+):(\d+)}')
    args = parseArgs()

    setlist = args.setlist
    folder, filename = os.path.split(setlist)
    song_folder = os.path.abspath(f"{folder}/..")

    with open(setlist, 'r') as f:
        titles = f.readlines()

    seconds = 0
    count = 0

    for title in titles:
        title = title.strip()

        if title.startswith('-'):
            continue

        with open(f"{song_folder}/{title}.txt") as f:
            text = f.read()
            if ((m := duration_prog.search(text)) is None):
                print(f"'{title}' has no duration metadata")
            else:
                count += 1
                print(f"{title}: {m.group(1)}:{m.group(2)}")
                seconds += int(m.group(1)) * 60 + int(m.group(2))

    hours = seconds // 3600
    seconds = (seconds - hours * 3600)
    minutes = seconds // 60
    seconds = seconds % 60
    print(f"{count} songs, total duration {hours:02d}:{minutes:02d}:{seconds:02d}")

if __name__ == '__main__':
    main()
