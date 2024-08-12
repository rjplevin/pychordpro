#!/usr/bin/env python3

# Optionally uses https://github.com/Pilfer/ultimate-guitar-scraper (as "ug")
# to download files from Ultimate Guitar.

import argparse
import sys
from collections import namedtuple
import os
import re

Chord = namedtuple('Chord', ['name', 'position'])
Chords = namedtuple('Chords', ['chords'])
Line = namedtuple('Line', ['chords', 'lyrics'])

def parseArgs():
    parser = argparse.ArgumentParser(description='Fix up exported Ultimate Guitar files for ChordPro conversion')

    parser.add_argument('-a', '--artist',
                        help='The song artist. Taken from file if present. Default is YYY.')

    parser.add_argument('-b', '--book', default='ZZZ',
                        help='The songbook this belongs to. Default is ZZZ.')

    parser.add_argument('-d', '--duration', default='3:30',
                        help='The song duration. Default is 3:30')

    parser.add_argument('-i', '--input',
                        help='The UG-format file to convert. Use "-i -" for stdin. '
                        'Required if not using --ug-id to download the file.')

    parser.add_argument('-m', '--tempo', default='120',
                        help='The song tempo. Default is 120')

    parser.add_argument('-n', '--no-backup', action='store_true',
                        help='Do not create a backup file')

    parser.add_argument('-o', '--output',
                        help='The output file. Default is to overwrite the input file.')

    parser.add_argument('-u', '--ug-id',
                        help='Run the ultimate-guitar-scraper (as "ug") using the given '
                             'song ID to download the UG-format file')

    parser.add_argument('-t', '--title',
                        help='The song title. Taken from file if present. Default is XXX.')


    args = parser.parse_args()
    return args

# e.g., "Song name: Althea  by  Grateful Dead"
song_pattern = r"^Song name: (.*)$"
song_prog = re.compile(song_pattern, flags=re.MULTILINE)

chord_pattern = r"([A-G][b\#]?)(sus|aug|dim|maj|min|ma|Ma|mi|M|m)?(2|4|5|6|7|9|11|13)?(/[A-G][b\#]?)?"
chord_prog = re.compile(chord_pattern)

def convert_to_objects(text):
    lines = text.split('\n')
    objs = []

    for line in lines:
        if re.match('^\s*$', line):
            objs.append('')   # insert a blank line
            continue

        # See if the line is all chords
        words = re.split('[-\s]+', line)
        is_chords = all(not word or chord_prog.match(word) for word in words) # ignore empty strings

        if is_chords:
            chords = Chords([Chord(name=m.group(0), position=m.start())
                             for m in re.finditer(chord_prog, line)])
            objs.append(chords)

        else:
            objs.append(line)

    final = []
    prev = None

    for obj in objs:
        if obj == '':
            if type(prev) is Chords:
                final.append(prev)

            if prev != '':  # avoid extra blank lines
                final.append('')

            prev = obj

        elif type(obj) is Chords:
            if prev:
                final.append(prev)  # not for embedding in lyrics

            prev = obj      # save this in case next line is lyrics

        else: # => obj is non-empty text

            if type(prev) is Chords:
                final.append(Line(chords=prev, lyrics=obj))
                prev = None
            else:
                final.append(obj)
                prev = None     # obj is not Chords

    if prev:
        # final line was Chords
        final.append(prev)

    return final

def convert_to_chordpro(text):
    objs = convert_to_objects(text)
    lines = []

    for lineno, obj in enumerate(objs):
        # print(f"{lineno}: {obj}")

        if type(obj) is Line:
            text = obj.lyrics

            # insert chords into lyrics in reverse order
            for chord in reversed(obj.chords.chords):
                name = chord.name
                pos = chord.position
                text = text[:pos] + f"[{name}]" + text[pos:]

        elif type(obj) is Chords:
            chords = ' '.join([chord.name for chord in obj.chords])
            text = f"[{chords}]"

        else: # text
            text = obj

        lines.append(text)

    revised = '\n'.join(lines)
    return revised


def main():
    metadata = '''{{title: {title}}}
{{artist: {artist}}}
{{tempo: {tempo}}}
{{duration: {duration}}}
'''

    args = parseArgs()

    title = args.title
    artist = args.artist

    make_backup = not (args.no_backup or args.output)

    file = args.input

    if args.ug_id:
        import subprocess
        cmd = f"ug fetch -id '{args.ug_id}'"
        bytes = subprocess.check_output(cmd, shell=True)
        text = bytes.decode("utf-8")

    elif file == '-':
        text = str(sys.stdin.read())

    else:
        if make_backup:
            backup = file + '~'
            os.rename(file, backup)     # create backup of original
            file = backup

        with open(file, 'r') as f:
            text = f.read()

    text = re.sub(r'\r\n', '\n', text, flags=re.MULTILINE)

    # seems this is not required with auto-download using ug program
    if file and file != '-':
        text = re.sub(r'\n\n', '\n', text)

    # extract title and artist from file, if present
    if (m := song_prog.search(text)):
        # delete the line
        text = re.sub(m.group(0), '', text)

        t, a = m.group(1).split("  by  ")
        title = title or t      # don't overwrite cmd line args
        artist = artist or a

    pattern = r'\[((Chorus|Verse|Bridge|Intro|Outro|Solo|Instrumental)\s*\d*)\]'
    text = re.sub(pattern, r'\1:', text)

    text = convert_to_chordpro(text)
    output = args.output or file

    with open(output, 'w') as f:
        if args.book:
            f.write(f"{{book: {args.book}}}\n")

        f.write(metadata.format(title=title or 'XXX',
                                artist=artist or 'YYY',
                                tempo=args.tempo,
                                duration=args.duration))
        f.write(text)

main()
