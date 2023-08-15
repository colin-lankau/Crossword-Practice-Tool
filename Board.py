class Board:


    def __init__(self, a_clues: list, a_answers: list, d_clues: list, d_answers: list, isSunday: bool):
        self.a_clues = a_clues
        self.a_answers = a_answers
        self.d_clues = d_clues
        self.d_answers = d_answers
        self.isSunday = isSunday
        self.length = 15 if not isSunday else 21
        self.board = [ [] for i in range(self.length) ]


    def __post_init__(self):
        self.build_Board()


    def __repr__(self):
        return_text = ""
        for row in self.board:
            for char in row:
                return_text += char
            return_text += "\n"
        return return_text


    def build_Board(self):
        '''
        Receives a list of tuples of (answer, clue) for both acrosses and downs.
        Builds the board into a 2d list of answers
        '''

        # generate the board through some sort of backtracking algorithm
        x, y = 0, 0
        for ac in self.a_clues:
            if len(ac) > self.length - x:

                y += 1
                x = 0
            self.add_to_Board(ac, x, y)
            x += len(ac)
    

    def add_to_Board(self, word: str, x: int, y: int):
        '''
        Receives word in string form, breaks it into chars, and adds it to board
        '''

        for char in word:
            self.board[x][y] = char
            x += 1

    
    def fill_black_squares(self, x: int, y: int):
        '''
        Fills in black squares if necessary to the end of the grid
        '''

        for i in range(x, self.length, 1):
            self.board[x][y] = "0"