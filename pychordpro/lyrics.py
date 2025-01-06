#!/usr/bin/env python3
#
# Output the lyrics only from a chordpro format file
# by stripping meta data, labels, and chords
#
import argparse
import os
import re

def parseArgs():
    parser = argparse.ArgumentParser(description='Output lyrics only from a chordpro format file')

    parser.add_argument('file', action='store', nargs='+', help='files to process')

    parser.add_argument('-o', '--output-dir', default=".", help='output directory')

    args = parser.parse_args()
    return args

def main():
    args = parseArgs()
    output_dir = args.output_dir or '.'
    files = args.file

    for file in files:
        basename = os.path.basename(file)
        output_file = os.path.join(output_dir, basename)

        with open(file) as f:
            lines = f.readlines()

        blank = False
        with open(output_file, 'w') as f:
            for line in lines:
                # skip labels
                if re.match(r'.*:\s*$', line):
                    print("Skipping label:", line)
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
