'''
This module is for creating a working concept for a mini grid generation algorithm
'''
# git add -- . :!backupCSVs/*  :!backupDBs/* :!LearningConcurrency/* :!LearningSQLite3/* :!10-06-23.txt :!Board.py :!crossword.db :!curBackup.sql :!main.py :!test.py :!__pycache__/*

import random
import sqlite3
import time
from collections import deque, defaultdict, OrderedDict
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
        self._previous_fills = deque() # if go back a state in the board, don't repull from database because we already did that
        self._previous_fills.append({})


    def reset(self) -> None:
        self._board = [ [ "_" if (j,i) not in self._shape else "-" for i in range(5) ] for j in range(5) ]
        self._previous_states.append(deepcopy(self._board))
    

    def __repr__(self) -> None:
        return_text = "\n  "
        for row in self._board:
            for char in row:
                return_text += f"{char}  "
            return_text += "\n  "
        return return_text

    
    def get_patterns(self, done=False) -> set:
        '''
        Utility function to get all patterns we want to check
        Needed to make sure the board doesn't have a dead fill, ie. cant be filled anymore
        Return a set of the patterns as we don't want to check the same patterns multiple times
        '''
        patterns = []
        # add horizontal patterns
        for row in self._board:
            if not done:
                if '_' not in row:
                    continue
            patterns.append(''.join(row))
        # add vertical patterns
        columns = [ ''.join([row[i] for row in self._board]) for i in range(5) ]
        for col in columns:
            if not done:
                if '_' not in col:
                    continue
            patterns.append(col)
        return set(patterns)

    
    def get_hardest_fills(self, con) -> dict:
        '''
        Get the hardset fills left in the board and return those
        '''
        fill_state = deepcopy(self._previous_fills[-1])
        # print(fill_state.keys())
        result, hardest = {}, float("inf")
        for i, pat in enumerate(self._board):
            pat = ''.join(pat)
            if '_' not in pat: # continue if word is done
                continue
            if pat in fill_state: # don't go out to database if we previously checked thius pattern last cycle
                possible_words = fill_state[pat]
            else:
                with con:
                    cur = con.cursor()
                    cur.execute(f"SELECT DISTINCT Answer FROM AnswerClueDB WHERE Answer LIKE '{pat}';")
                    possible_words = [ row[0] for row in cur.fetchall()]
                    fill_state[pat] = possible_words
            if len(possible_words) < hardest:
                hardest = len(possible_words)
                result = {
                    'direction': 'across',
                    'pat': pat,
                    'possible_words': possible_words,
                    'index': i
                }
        columns = [ ''.join([row[i] for row in self._board]) for i in range(5) ]
        for i, pat in enumerate(columns):
            if '_' not in pat: # continue if word is done
                continue
            if pat in fill_state: # don't go out to database if we previously checked thius pattern last cycle
                possible_words = fill_state[pat]
            else:
                with con:
                    cur = con.cursor()
                    cur.execute(f"SELECT DISTINCT Answer FROM AnswerClueDB WHERE Answer LIKE '{pat}';")
                    possible_words = [ row[0] for row in cur.fetchall()]
                    fill_state[pat] = possible_words
            if len(possible_words) < hardest:
                hardest = len(possible_words)
                result = {
                    'direction': 'down',
                    'pat': pat,
                    'possible_words': possible_words,
                    'index': i
                }
        # print(result)
        self._previous_fills.append(fill_state)
        return result  


    def fill_board(self, word: str, direction: str, index: int) -> None:
        '''
        Fill word into desired space on board
        '''
        counter = 0
        if direction == 'across':
            for i in range(0, 5, 1):
                self._board[index][i] = word[counter]
                counter += 1
        else:
            for i in range(0, 5, 1):
                self._board[i][index] = word[counter]
                counter += 1


    def check_completion(self, con) -> bool:
        '''
        Checks if board is finished or not
        '''
        # do one final check of all the answers
        # print("Checking Completion")
        patterns = self.get_patterns(True)
        for pat in patterns:
            with con:
                cur = con.cursor()
                cur.execute(f"SELECT COUNT(*) FROM AnswerClueDB WHERE Answer='{pat}';")
                count = cur.fetchone()[0]
                # print(f"Pattern: {pat}, Count: {count}")
                if count == 0:
                    return False
        return True

    
    def generate_grid(self) -> None:
        '''
        General idea is for a backtracking algorithm
        We want to keep a 2d dp array to find the next best fillin spot
            - this will be weighted by some score that will consist of closest to the upper left corner and number of chars to the left or above of current space
        '''
        # step 0 - initiate connection to database
        con = sqlite3.connect('crossword.db')

        # step 1 - begin loop and initialize
        attempt_counter = defaultdict(int)
        self._previous_states.append(deepcopy(self._board))
        # add and statement here to check all words on board are in db
        while any('_' in row for row in self._board):

            # print("New Iteration of loop")
            # print("Current Board:")
            # print(self)
            # print("Previous States")
            # print(self._previous_states)

            # new step 2 - get hardset fills left for acrosses and downs
            # print("Step 2- Get Hardest Fills")
            data = self.get_hardest_fills(con)

            # step 3 - make sure we aren't infinite looping
            # print("Step 3- Choose word")
            outer_flag = False
            for attempt_no in itertools.count():
                chosen_word = random.choice(data['possible_words'])
                # print(f"Attempt {attempt_no} -- {chosen_word}")
                if attempt_counter[chosen_word] <= 2:
                    break
                if attempt_no > 10 and attempt_counter[chosen_word] > 1:
                    # print("No new words to try, returning to previous state")
                    try: # go back 1 state
                        self._board = self._previous_states.pop()
                        self._previous_fills.pop()
                    except:
                        print("RESET-1")
                        self.reset() # if we pop from an empty queue, simply restart
                        attempt_counter.clear()
                    outer_flag = True
                    break
            if outer_flag:
                continue

            # step 4 - fill word onto board
            # print("Step 4- Fill word onto board")
            self.fill_board(chosen_word, data['direction'], data['index'])
            attempt_counter[chosen_word] += 1

            # step 5 - get patterns left on the board, if the board is full, check for existence of every word in db
            # print(f"\n  ----- Beginning Step 5 -----  ")
            # print(f"Current board:\n{self}")
            # print("Step 5- check completion")
            patterns = self.get_patterns()
            flag = True
            # print(f"patterns: {patterns}")
            if len(patterns) == 0: # the board has no _ squares
                finished = self.check_completion(con)
                if finished: 
                    break
                else:
                    flag = False
            else: # board has at least one _ square
                for pat in patterns:
                    with con:
                        cur = con.cursor()
                        cur.execute(f"SELECT DISTINCT Answer FROM AnswerClueDB WHERE Answer LIKE '{pat}';")
                        possible_words = [ row[0] for row in cur.fetchall()]
                        if len(possible_words) == 0: # case 1 - pattern doesn't exist in database -> return to previous board state
                            flag = False
                            break
                        else: # case 2 - all patterns exist in database -> do nothing
                            # print(f"Pattern {pat} still have {len(possible_words)} viable fills")
                            pass
            if not flag:
                # print(f"NO MORE POSSIBLE FILLS FOR {pat}... return board to previous state")
                try:
                    self._board = self._previous_states.pop()
                    self._previous_fills.pop()
                except:
                    print("RESET-2")
                    self.reset() # if we pop from an empty queue, simply restart
                    attempt_counter.clear()
            
            # print the queue
            # for i, state in enumerate(self._previous_states):
                # print(f"State {i}\n{state}")

            self._previous_states.append(deepcopy(self._board))


if __name__ == "__main__":
    # single test - time varies wildly
    # mini = Mini()
    # start = time.time()
    # mini.generate_grid()
    # runtime = start - time.time()
    # print(f"{mini}{runtime}s\n")
    # time test - 10 grids - 5466s - least = 57s - most = 1539s
    # time test w/ pattern storage - 10 grids - 3808s - least = 22s - most = 1446s
        # subsequent tries - 2010s - 2866s
    grids = [Mini() for _ in range(10)]
    times = []
    for i, g in enumerate(grids):
        start = time.time()
        g.generate_grid()
        runtime = start - time.time()
        times.append(runtime)
        print(f"Finished grid {i}\n{g}{runtime}s")
    print(f"Total time to generate {len(grids)} grids: {sum(times)}s")