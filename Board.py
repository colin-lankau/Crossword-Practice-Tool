class Board:


    def __init__(self, a_clues: list, a_answers: list, d_clues: list, d_answers: list, isSunday: bool):
        self.a_clues = list(a_clues)
        self.a_answers = list(a_answers)
        self.d_clues = list(d_clues)
        self.d_answers = list(d_answers)
        self.isSunday = isSunday
        self.length = 15 if not isSunday else 21
        self.board = [ [] for i in range(self.length) ]


    def __repr__(self):
        return_text = "| "
        for row in self.board:
            for char in row:
                return_text += f"{char} | "
            return_text.rstrip(" | ")
            return_text += "\n"
            return_text += '-' * 65
            return_text += "\n| "
        return return_text


    def build_Board(self):
        '''
        Receives a list of tuples of (answer, clue) for both acrosses and downs.
        Builds the board into a 2d list of answers
        '''

        # generate the board through some sort of backtracking algorithm
        x, y = 0, 0
        for ac in self.a_answers:
            print(ac)
            print()
            print(self.board)
            print()
            if len(ac) > self.length - x:
                y += 1
                x = 0
                self.add_to_Board(ac, y)
            else:
                self.add_to_Board(ac, y)
            x += len(ac)
            self.fill_black_squares(y)
    

    def add_to_Board(self, word: str, row: int):
        '''
        Receives word in string form, breaks it into chars, and adds it to board
        '''

        for char in word:
            self.board[row].append(char)

    
    def fill_black_squares(self, row: int):
        '''
        Fills in black squares if necessary to the end of the grid
        '''

        self.board[row].append("~")