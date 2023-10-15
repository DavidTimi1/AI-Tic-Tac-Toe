import random
from termcolor import colored as color
from sys import exit


INFINITY = float("inf")


class TicTacToeGame():
    def __init__(self, arr=[]):
        if not len(arr):
            self.table = [
                ["", "", ""],
                ["", "", ""],
                ["", "", ""]
            ]
            self.turn = "X"
            self.plays = 0

        else:
            if len(arr) != 3:
                raise Exception("Incomplete Board")
            for row in arr:
                if len(row) != 3:
                    raise Exception("Incomplete Board")

            # if the board is complete
            self.table = arr
            self.turn, self.plays = self.evaluate_turn()
        self.solution = None

    def __str__(self):
        arr = []
        for i, row in enumerate(self.table):
            val = []
            sol = self.solution

            if sol:
                [val.append(color(cell, 'green') if (i, j) in sol else cell) for j, cell in enumerate(row)]

            elif sol is False:
                [val.append(color(cell, 'yellow')) for cell in row]

            else:
                val = row

            row_string = (val[0] if val[0] else " ") + " | " + (val[1] if val[1] else " ") + " | " + (val[2] if val[2] else " ")
            
            arr.append(row_string)
        string = "\n"+"\n------------\n".join(arr)+"\n"
        return string

    def evaluate_turn(self, table=None):
        # if no table was provided use default
        if table is None:
            table = self.table

        content = str(table)
        x_plays = content.count("X")
        o_plays = content.count("O")

        max_plays = max(x_plays, o_plays)
        min_plays = min(x_plays, o_plays)

        # difference in play can only be 1 or less and o cannot have more plays than x
        if o_plays > x_plays or max_plays - min_plays > 1:
            raise Exception("Invalid Board")

        turn = "X" if max_plays == min_plays else "O"
        plays = max_plays + min_plays
        return (turn, plays)

    def play(self, pos, board=None, turn=None):
        # if no turn and board were not provided use default
        if turn is None:
            board = self.table
            turn = self.turn

        row, col = pos
        if board[row][col]:
            raise Exception("Already played there!")

        board[row][col] = turn

    def __update__(self):
        self.plays += 1
        self.turn = "O" if self.plays % 2 else "X"

    def get_actions(self, table=None):
        """
        Gets cells that are empty in a given table
        """
        available = []
        if table is None:
            table = self.table

        for i, row in enumerate(table):
            for j, cell in enumerate(row):
                if not cell:
                    available.append((i, j))
        return available

    def checkStatus(self, pos, table=None, turn=None, steps=None):
        """
        Checks whether the state of the game is terminal
        """
        row, col = pos
        sim = True

        if turn is None:
            sim = False
            table = self.table
            turn = self.turn
            steps = self.plays

        utility = 1 if turn == "X" else -1
        try:
            utility *= 1/steps
        except ZeroDivisionError:
            return

        # optimized check for column and row
        if table[row][0] == table[row][1] == table[row][2] == turn:
            if not sim:
                self.solution = [(row, 0), (row, 1), (row, 2)]
            return utility

        if table[0][col] == table[1][col] == table[2][col] == turn:
            if not sim:
                self.solution = [(0, col), (1, col), (2, col)]
            return utility

        if table[0][0] == table[1][1] == table[2][2] == turn:
            if not sim:
                self.solution = [(0, 0), (1, 1), (2, 2)]
            return utility

        if table[0][2] == table[1][1] == table[2][0] == turn:
            if not sim:
                self.solution = [(0, 2), (1, 1), (2, 0)]
            return utility

        if len(self.get_actions(table)) < 1:
            if not sim:
                self.solution = False
            return 0

    def simulate(self):
        """
        Simulates the best play in the game given the state
        """

        all_actions = self.get_actions()

        v = -INFINITY if self.turn == "X" else INFINITY
        best = None

        while len(all_actions):
            sim_table = []
            [sim_table.append(row.copy()) for row in self.table]

            action = random.choice(all_actions)
            all_actions.remove(action)

            if self.turn == "X":
                x = self.min_outcome(self.turn, sim_table, action, 0, v)
                w = max(v, x)

            else:
                x = self.max_outcome(self.turn, sim_table, action, 0, v)
                w = min(v, x)

            if v != w:
                v = w
                best = action

        self.play(best)
        game_stat = self.checkStatus(best)
        self.__update__()

        if game_stat is not None:
            self.end_game(game_stat)
            return 1

    def max_outcome(self, turn, table, action, plays, cur_min):
        self.play(action, table, turn)
        plays += 1

        utility = self.checkStatus(action, table, turn, plays)
        if utility is not None:
            # print("max", plays, cur_min)
            return utility

        turn = "O" if turn == "X" else "X"

        v = -INFINITY
        all_actions = self.get_actions(table)

        for action in all_actions:
            copy_table = []
            [copy_table.append(row.copy()) for row in table]

            outcome = self.min_outcome(turn, copy_table, action, plays, v)
            v = max(v, outcome)
            if v > cur_min:
                break
        return v

    def min_outcome(self, turn, table, action, plays, cur_max):
        self.play(action, table, turn)
        plays += 1

        utility = self.checkStatus(action, table, turn, plays)
        if utility is not None:
            # print("min", plays, cur_max)
            return utility

        turn = "O" if turn == "X" else "X"

        v = INFINITY
        all_actions = self.get_actions(table)

        for action in all_actions:
            copy_table = []
            [copy_table.append(row.copy()) for row in table]

            outcome = self.max_outcome(turn, copy_table, action, plays, v)
            v = min(v, outcome)
            if v < cur_max:
                break

        return v

    def play_all(self):
        ended = None
        while ended is None:
            ended = self.simulate()

    def end_game(self, utility):
        print(color("Game has Ended!\n", 'magenta'))
        if utility > 0:
            print(color("X wins!", 'green'))
        elif utility == 0:
            print(color("Tie!", 'yellow'))
        else:
            print(color("O wins!", 'green'))
        print(self)


def parse_input(string):
    try:
        arr = string.split(",")
        if len(arr) > 2:
            raise Exception()
        res = (int(arr[0]), int(arr[1]))
    except Exception:
        raise Exception("Position should be in format (row,col)")
    else:
        return res


xando = TicTacToeGame()
print(xando)
side = input("Which side are you (X / O)? ")
while not(side == "X" or side == "O"):
    side = input(color("Which side are you (X / O)? ", 'yellow'))

if side == "O":
    game_ending = xando.simulate()
    print(xando)
    if game_ending is not None:
        exit(0)

while True:
    string = input(f"Play {xando.turn} at position (row, column): ")
    pos = parse_input(string)

    while pos not in xando.get_actions():
        print(color("Already played there!", 'yellow'))
        string = input(f"Play {xando.turn} at position (row, column): ")
        pos = parse_input(string)

    xando.play(pos)
    print(xando)
    game_stat = xando.checkStatus(pos)
    xando.__update__()

    if game_stat is not None:
        xando.end_game(game_stat)
        break

    if xando.simulate() is not None:
        break
    print(xando)

# xando.play_all()
