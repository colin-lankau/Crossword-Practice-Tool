# Crossword Practice Tool

A plan for this to be a tool to be useful for those wanting to get better at NYT crosswords.

## Current Features

- Scrape.py - web scrapes for answer clue data
- DatabaseFunctions.py - Manages and updates database and backups
- miniBoard.py - class for 5x5 board, contains algorithm for generation

## TODO

- FIX RESET BUG - this should greatly increase performance when I can track down the cause
- Improve performance of crossword generation algorithm
- Finish clue functionality after grid creation
- Cleanup the code for miniBoard.py
- Once miniBoard puzzle creation is working (efficiently), expand base algorithm for 10x10 or 15x15 puzzle
- Learn both FastAPI and React
- Turn into a FastAPI application, set up with user registration, and many features for practicing crossword solving
- Develop a front end for the application with React
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
* 0.4
    * miniBoard generation algorithm now works with varying puzzle structure