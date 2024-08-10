#!/usr/bin/env python3

import argparse
from collections import namedtuple
import os
import re

Chord = namedtuple('Chord', ['name', 'position'])
Chords = namedtuple('Chords', ['chords'])
Line = namedtuple('Line', ['chords', 'lyrics'])

def parseArgs():
    parser = argparse.ArgumentParser(description='Fix up exported Ultimate Guitar files for ChordPro conversion')

    parser.add_argument('files', nargs='+', help='The files to tweak')

    parser.add_argument('-a', '--artist', default='YYY',
                        help='The song artist. Default is YYY.')

    parser.add_argument('-d', '--duration', default='3:30',
                        help='The song duration. Default is 3:30')

    parser.add_argument('-m', '--tempo', default='120',
                        help='The song tempo. Default is 120')

    parser.add_argument('-n', '--no-backup', action='store_true',
                        help='Do not create a backup file')

    parser.add_argument('-o', '--output',
                        help='The output file. Default is to overwrite the input file.')

    parser.add_argument('-t', '--title', default='XXX',
                        help='The song title. Default is XXX.')


    args = parser.parse_args()
    return args

chord_pattern = r"([A-G][b\#]?)(sus|aug|dim|maj|min|ma|Ma|mi|M|m)?(2|4|5|6|7|9|11|13)?(/[A-G][b\#]?)?"
chord_prog = re.compile(chord_pattern)

def convert_to_objects(text):
    lines = text.split('\n')

    objs = []
    obj = None

    for line in lines:
        if line == '':
            objs.append(line) # insert a blank line
            obj = None        # don't treat as lyrics
            continue

        # See if the line is all chords
        words = re.split('[-\s]+', line)
        is_chords = all(not word or chord_prog.match(word) for word in words) # ignore empty strings

        if is_chords:
            obj = Chords([Chord(name=m.group(0), position=m.start())
                          for m in re.finditer(chord_prog, line)])
        else:
            obj2 = line

            # If previous object is Chords, join them as a Line tuple
            if obj2 and type(obj) is Chords:
                obj = Line(chords=obj, lyrics=obj2)
            else:
                obj = obj2

        objs.append(obj)

    return objs

def convert_to_chordpro(text):
    objs = convert_to_objects(text)
    lines = []

    for lineno, obj in enumerate(objs):
        print(f"{lineno}: {obj}")

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


metadata = '''{{book: Sing-along}}
{{title: {title}}}
{{artist: {artist}}}
{{tempo: {tempo}}}
{{duration: {duration}}}

'''

def main():

    args = parseArgs()

    if args.output is not None and len(args.files) > 1:
        raise Exception("You can specify output name when processing one file only.")

    make_backup = not (args.no_backup or args.output)

    for file in args.files:

        if make_backup:
            backup = file + '~'
            os.rename(file, backup)     # create backup of original
            input = backup
        else:
            input = file

        with open(input, 'r') as f:
            text = f.read()

        revised = re.sub('\n\n', '\n', text, flags=re.MULTILINE)

        pattern = r'\[((Chorus|Verse|Bridge|Intro|Outro|Solo|Instrumental)\s*\d*)\]'
        revised = re.sub(pattern, r'\1:', revised)

        revised = convert_to_chordpro(revised)
        output = args.output or file

        with open(output, 'w') as f:
            f.write(metadata.format(title=args.title,
                                    artist=args.artist,
                                    tempo=args.tempo,
                                    duration=args.duration))
            f.write(revised)

main()
