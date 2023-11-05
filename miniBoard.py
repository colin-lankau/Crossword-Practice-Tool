'''
This module is for creating a working concept for a mini grid generation algorithm
'''
# git add -- . :!backupCSVs/*  :!backupDBs/* :!LearningConcurrency/* :!LearningSQLite3/* :!10-06-23.txt :!Board.py :!crossword.db :!curBackup.sql :!main.py :!test.py :!__pycache__/*

import random
import sqlite3
import time
from collections import deque, defaultdict
from copy import deepcopy
import itertools

POSSIBLE_GRIDS = (
    (), # no black squares
    ( (4,3), (4,4) ), # black squares at location 4,3 and 4,4
    ( (0,4), (4,4) ),
    ( (0,0), (4,4) ),
    ( (0,4), (4,0) ),
    ( (0,4), (1,4) ),
    ( (0,0), (1,0), (3,4), (4,4) ),
    ( (0,0), (0,1), (3,4), (4,4) ),
    ( (0,0), (1,0), (0,4), (1,4) ),
    ( (0,0), (0,1), (4,3), (4,4) ),
    ( (0,3), (0,4), (4,0), (4,1) ),
    ( (0,0), (0,4), (4,0), (4,4) ),
    ( (0,4), (1,4), (3,0), (4,0) ),
    ( (0,3), (0,4), (1,4), (3,0), (4,0), (4,1) )
)

class Mini:


    def __init__(self) -> None:
        # self._shape = random.choices(POSSIBLE_GRIDS)[0]
        self._shape = POSSIBLE_GRIDS[0]
        self._board = [ [ "_" if (j,i) not in self._shape else "-" for i in range(5) ] for j in range(5) ]
        self._answers = set()
        self._previous_states = deque()
    

    def __repr__(self) -> None:
        return_text = "\n  "
        for row in self._board:
            for char in row:
                return_text += f"{char}  "
            return_text += "\n  "
        return return_text


    def get_weights(self) -> None:
        '''
        Utility function that returns a dictionary like so:
            weights = {
                (0, 0): 0      -> 0 signifies already filled in square
                (0, 1): 0 
                ...
                (1, 0): 9      -> 9 would signify some weight
            }
        Weight is calculated with distance to top left and number of adjacent filled squares
        '''
        weights = {}
        dp = [ [ 0 for _ in range(5) ] for _ in range(5) ]
        for i, row in enumerate(self._board):
            for j, col in enumerate(row):
                if col == '-': # black square
                    result = 0
                elif col != '_': # letter in space
                    result = 1
                else: # letter not in space
                    result = 0
                    if i != 0 and self._board[i-1][j] not in ['-', '_']:
                        result += dp[i-1][j]
                    if j != 0 and self._board[i][j-1] not in ['-', '_']:
                        result += dp[i][j-1]
                    result += (15 - i - j)
                dp[i][j] = result
                weights[(i,j)] = dp[i][j]
        return weights


    def choose_direction(self, position: tuple) -> str:
        '''
        Utility function that chooses a fill direction, either across or down
        Higher weights are:
            - being closer to done
            - containing rare letters
        '''
        letter_value = {'A':1, 'B':3, 'C':3, 'D':2, 'E':1, 'F':4, 'G':2, 'H':4, 'I':1,
                'J':8, 'K':5, 'L':1, 'M':3, 'N':1, 'O':1, 'P':3, 'Q':10, 'R':1,
                'S':1, 'T':1, 'U':1, 'V':8, 'W':4, 'X':8, 'Y':4, 'Z':10}
        row, col = position
        # keep column consistent and see what is on rows above and below
        above_row, below_row, vertical_weight, vertical_structure = 0, 0, 0, f"{self._board[row][col]}"
        while True:
            if row+above_row != 0 and self._board[row+above_row-1][col] != '-':
                above_row -= 1
                vertical_structure = self._board[row+above_row][col] + vertical_structure
            else:
                break
        for i in range(row-1, row+above_row-1, -1):
            if self._board[i][col] not in ['-', '_']:
                vertical_weight += letter_value[self._board[i][col]] + 1
            else:
                vertical_weight += 1
        while True:
            if row+below_row != 4 and self._board[row+below_row+1][col] != '-':
                below_row += 1
                vertical_structure += self._board[row+below_row][col]
            else:
                break
        for i in range(row+1, row+below_row+1, 1):
            if self._board[i][col] not in ['-', '_']:
                vertical_weight += letter_value[self._board[i][col]] + 1
            else:
                vertical_weight += 1
        # keep row consistent and see what is on columns left and right
        left_col, right_col, horizontal_weight, horizontal_structure = 0, 0, 0, f"{self._board[row][col]}"
        while True:
            if col+left_col != 0 and self._board[row][col+left_col-1] != '-':
                left_col -= 1
                horizontal_structure = self._board[row][col+left_col] + horizontal_structure
            else:
                break
        for i in range(col-1, col+left_col-1, -1):
            if self._board[row][i] not in ['-', '_']:
                horizontal_weight += letter_value[self._board[row][i]] + 1
            else:
                horizontal_weight += 1
        while True:
            if col+right_col != 4 and self._board[row][col+right_col+1] != '-':
                right_col += 1
                horizontal_structure += self._board[row][col+right_col]
            else:
                break
        for i in range(col+1, col+right_col+1, 1):
            if self._board[row][i] not in ['-', '_']:
                horizontal_weight += letter_value[self._board[row][i]] + 1
            else:
                horizontal_weight += 1
        # print(f"Vertical Weight = {vertical_weight}")
        # print(f"Horizontal Weight = {horizontal_weight}")
        return ("across", horizontal_structure) if horizontal_weight >= vertical_weight else ("down", vertical_structure)


    def fill_word(self, dir, start, end, constant, chosen_word) -> None:
        '''
        Utility function to fill in the word to the correct position in the board
        '''
        counter = 0
        if dir == 'across':
            for i in range(start, end, 1):
                self._board[constant][i] = chosen_word[counter]
                counter += 1
        else:
            for i in range(start, end, 1):
                self._board[i][constant] = chosen_word[counter]
                counter += 1

    
    def get_patterns(self) -> set:
        '''
        Utility function to get all patterns we want to check
        Needed to make sure the board doesn't have a dead fill, ie. cant be filled anymore
        Return a set of the patterns as we don't want to check the same patterns multiple times
        '''
        patterns = []
        # add horizontal patterns
        for row in self._board:
            patterns.append(''.join(row))
        # add vertical patterns
        columns = [ ''.join([row[i] for row in self._board]) for i in range(5) ]
        for col in columns:
            patterns.append(col)
        return set(patterns)

    
    def generate_grid(self) -> None:
        '''
        General idea is for a backtracking algorithm
        We want to keep a 2d dp array to find the next best fillin spot
            - this will be weighted by some score that will consist of closest to the upper left corner and number of chars to the left or above of current space
        '''
        # step 0 - initiate connection to database
        con = sqlite3.connect('crossword.db')

        # step 1 - begin loop
        attempt_counter = defaultdict(int)
        # add and statement here to check all words on board are in db
        while any('_' in row for row in self._board):

            print("New Iteration of loop")

            # step 2 - get priority score for each filled square in grid, then determine whether to fill across or down
            weights = self.get_weights()
            best_position = max(weights, key=weights.get)
            direction, structure = self.choose_direction(best_position)

            # step 3 - get possible fill words
            with con:
                cur = con.cursor()
                cur.execute(f"SELECT DISTINCT Answer FROM AnswerClueDB WHERE Answer LIKE '{structure}';")
                possible_words = [ row[0] for row in cur.fetchall()]
            # print(possible_words)

            # step 4 - choose a word from possible_words
                # loop through until we find a word that has been tried 2 or less times while building the board
                # if no such word exists, return a previous state and repeat loop
            outer_flag = False
            for attempt_no in itertools.count():
                if attempt_no > 1000:
                    print("No new words to try, returning to previous state after 1000 attempts")
                    self._board = self._previous_states.pop()
                    outer_flag = True
                    break
                chosen_word = random.choice(possible_words)
                if attempt_counter[chosen_word] <= 2:
                    break
            if outer_flag:
                continue

            # step 5 - Fill chosen word into our miniBoard object, the increment the word we chose in our attempt_counter dict
            # if len(possible_words) == 0:
            #     print("No possible words found in the DB")
            #     break
            start, end = 0, 5
            constant = best_position[0] if direction == 'across' else best_position[1]
            self.fill_word(direction, start, end, constant, chosen_word)
            attempt_counter[chosen_word] += 1

            # step 6 - check puzzle to see if any patterns are unfillable
                # case 1 - pattern doesn't exist in database -> return to previous board state
                # case 2 - all patterns exist in database -> do nothing
                # after both cases repeat loop
                # have some way to check if we are stuck in an unfinishable scenario
            print(f"\n  ----- Beginning Step 5 -----  ")
            print(f"Current board:\n{self}")
            patterns = self.get_patterns()
            flag = True
            print(f"patterns: {patterns}")
            for pat in patterns:
                with con:
                    cur = con.cursor()
                    cur.execute(f"SELECT DISTINCT Answer FROM AnswerClueDB WHERE Answer LIKE '{pat}';")
                    possible_words = [ row[0] for row in cur.fetchall()]
                    if len(possible_words) == 0:
                        print(f"NO MORE POSSIBLE FILLS FOR {pat}... return board to previous state")
                        self._board = self._previous_states.pop()
                        flag = False
                        break
                    else:
                        print(f"Pattern {pat} still have {len(possible_words)} viable fills")
            if flag:
                print("Board still remains completable")

            
            # print the queue
            for i, state in enumerate(self._previous_states):
                print(f"State {i}\n{state}")

            self._previous_states.append(deepcopy(self._board))


if __name__ == "__main__":
    mini = Mini()
    print(mini)
    mini.generate_grid()
    print(mini)