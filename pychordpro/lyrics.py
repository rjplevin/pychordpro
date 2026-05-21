#!/usr/bin/env python3
#
# Output the lyrics only from a chordpro format file
# by stripping meta data, labels, and chords
#
# Read output into TextToPDF.app, order them, export a single PDF.
#
import argparse
import os
import re

def parseArgs():
    parser = argparse.ArgumentParser(description='Output lyrics only from a chordpro format file')

    parser.add_argument('file', action='store', nargs='*', help='files to process')

    parser.add_argument('-i', '--input-dir', default=".", help='input directory containing files')

    parser.add_argument('-o', '--output-dir', default=".", help='output directory')

    parser.add_argument('-s', '--set-list', help='Set list file specifying song file names')

    args = parser.parse_args()
    return args

def main():
    args = parseArgs()
    output_dir = args.output_dir

    set_list = args.set_list
    if set_list:
        with open(set_list) as f:
            files = [file.strip() for file in f.readlines() if not file.startswith('---')]
            files = [f'{file}.txt' for file in files]
    else:
        if not args.file:
            raise Exception('No input files or setlist specified')

        files = args.file

    # interpret all files relative to given input dir or "."
    files = [os.path.join(args.input_dir, file) for file in files]

    print(files)

    include_labels = True        # testing this; maybe make argument

    number = 1  # number the songs so they sort into setlist order

    for file in files:
        basename = os.path.basename(file)
        output_file = os.path.join(output_dir, f'{number:02d} {basename}')
        number += 1

        with open(file) as f:
            lines = f.readlines()

        blank = False
        grid = False
        with open(output_file, 'w') as f:
            # Insert song title without the final ".txt"
            f.write(f'*** {basename[0:-4]} ***\n')

            for line in lines:
                if not include_labels:
                    # skip labels
                    if re.match(r'.*:\s*$', line):
                        print("Skipping label:", line)
                        continue

                if re.match(r'\{sog', line):
                    grid = True
                    print("Start grid")
                    continue

                if re.match(r'\{eog', line):
                    grid = False
                    print("End grid")
                    continue

                if grid:
                    # ignore contents of grid
                    continue

                if re.match(r'\{.*\}\s*$', line):
                    print("Skipping directive:", line)
                    continue


                line = re.sub(r'\[.*?\]', '', line)

                line = line.strip()
                if not line:
                    if blank:
                        continue    # don't write out multiple blank lines
                    blank = True
                else:
                    blank = False

                f.write(f"{line}\n")

main()
