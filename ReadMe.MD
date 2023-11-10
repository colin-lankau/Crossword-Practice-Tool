# Crossword Practice Tool

A plan for this to be a tool to be useful for those wanting to get better at NYT crosswords.

## Current Features

- Scrape.py - web scrapes for answer clue data
- DatabaseFunctions.py - Manages and updates database and backups
- miniBoard.py - class for 5x5 board, contains algorithm for generation

## TODO

- Improve performance of crossword generation algorithm
- Implement a variety of layouts to the class
- Add clue functionality after grid creation
- Once miniBoard puzzle creation is working (efficiently), expand base algorithm for 10x10 or 15x15 puzzle
- Possibly turn into a django or flask application, set up with user registration, and many features for practicing crossword solving
- Improve performance of Scrape.py using multiprocessing

## Authors

[@Colin-Lankau](https://www.linkedin.com/in/colin-lankau/)

## Version History

* 0.1
    * Initial Release
* 0.2
    * miniBoard and Database introduction
* 0.3
    * massive improvement on miniBoard generation