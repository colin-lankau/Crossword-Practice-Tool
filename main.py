from Board import Board
import os
from datetime import date, datetime
from Scrape import Scrape
from unidecode import unidecode

# check if clues have already been scraped today, if false, scrape them and add to {today}.txt
year, month, day = str(date.today()).split("-")
today = f"{month}-{day}-{year[-2:]}"

if not os.path.isfile(f"{today}.txt"):

    across_clues, across_answers, down_clues, down_answers = Scrape(today)

    with open(f"{today}.txt", "a") as f:
        f.write(f"Across Clues:{len(across_clues)}\n")
        for ac in across_clues:
            f.write(f'''{unidecode(ac)}\n''')
        f.write(f"Across Answers:{len(across_answers)}\n")
        for aa in across_answers:
            f.write(f'''{unidecode(aa)}\n''')
        f.write(f"Down Clues:{len(down_clues)}\n")
        for dc in down_clues:
            f.write(f'''{unidecode(dc)}\n''')
        f.write(f"Down Answers:{len(down_answers)}\n")
        for da in down_answers:
            f.write(f'''{unidecode(da)}\n''')

# if clues have already been scraped, read from text file
else:
    lines = []
    with open(f"{today}.txt", "r") as f:
        for line in f.readlines():
            lines.append(line)

    print(f"Lines: {lines}")

    cur_line, cur_tag = 0, 0
    tag_lists = [ [] for i in range(4) ]
    while cur_line < len(lines):
        length = int(lines[cur_line].split(":")[1].rstrip())
        print(f"Length: {length} ... cur_line: {cur_line} ... cur_tag: {cur_tag}")
        cur_line += 1
        for i in range(cur_line, cur_line+length, 1):
            tag_lists[cur_tag].append(lines[i].rstrip())
        print(f"Tag_List at {cur_tag} is {tag_lists[cur_tag]}")
        cur_tag += 1
        cur_line += length
    
    across_clues, across_answers, down_clues, down_answers = tag_lists[0], tag_lists[1], tag_lists[2], tag_lists[3]

board = Board(across_clues, across_answers, down_clues, down_answers, datetime.today().strftime('%A') == 'Sunday')
board.build_Board()
print(board)