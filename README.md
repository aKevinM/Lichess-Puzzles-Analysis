# Lichess-Puzzles-Analysis

This directory contains four Python scripts used to prepare the Lichess database (games and puzzles), 1 .do file to run in STATA and 3 sample .csv files from the Lichess Database.

Summary

- Extract_PGN.py: Converts a PGN file into a .csv file with columns for opening, White Elo, and Black Elo.
- Clean_Puzzles.py: Cleans the Lichess puzzles database by removing rows without OpeningTags. This speeds up the Matcher_Ouvertures.py process.
- Clean_Part2.py: Lists the puzzles that were removed by Nettoyer_Puzzles.py (so they can be appended in STATA later).
- Match_Opening.py: Normalizes the OpeningTags field of puzzles by mapping it to real openings extracted from the game analysis database. This allows merging the two datasets by opening.

Requirements

- ~150GB of free disk space
- Python 3.12
- PeaZip (for Windows)

Steps

- Go to: https://database.lichess.org/#standard_games and download the games for August 2025.
- Go to: https://database.lichess.org/#puzzles and download the puzzle file.
- Decompress the files (using PeaZip on Windows).
- Run Extract_PGN.py.
- Run Clean_Puzzles.py.
- Run Clean_Part2.py.
- Run Match_Opening.py.
- Run the .do file in STATA. Warning: STATA is a paid service. Instead, you can use R or Python: just ask some AI to convert the .DO file into anything else free to use.

Notes

- The opening matching is not perfect. It keeps only the openings that are easiest to match and often removes opening variations.
- The .do file is in french. Sorry for the inconvenience.
