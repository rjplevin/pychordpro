# pychordpro

Convert songs from Ultimate Guitar format (chords above lyrics) to ChordPro format (chords embedded in lyrics).

This script is not intended to be comprehensive and complete. Rather, it provides a "pretty close"
version of the song in ChordPro format that can be edited a little to meet my (and perhaps your) needs.

The meta-data inserted at the top of the file is designed to work with 
[https://www.liveprompter.com/](LivePrompter 2). Command-line arguments allow you to provide
the song duration, tempo, and "book" the song should be part of.

This script can process a downloaded text file, or, more conveniently, use the
[ultimate-guitar-scraper](https://github.com/Pilfer/ultimate-guitar-scraper) 
to scrape the necessary bit from the Ultimate Guitar page of interest.

To use ultimate-guitar-scraper:

1. Clone and build [ultimate-guitar-scraper](https://github.com/Pilfer/ultimate-guitar-scraper)
2. Set the environment variable "UG" to the path do the ultimate-guitar-scraper executable.

Then, to process a song, search for the song file on
[https://www.ultimate-guitar.com/](Ultimate Guitar) and copy the numeric portion 
of the URL to pass to the script's `-u` / `--ug-id` flag.

By default, the title and artist name are extracted from the file, and
the title (plus '.txt') is used for the file name to save to. 

See the help text (`-h` / `--help`) for more information.
