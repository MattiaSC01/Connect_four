import numpy as np
import pygame as pg
import sys
import math
import time


DEPTH = 10

SIDE = 100
RADIUS = 40
SIZE = (7 * SIDE, 6 * SIDE)

COLOR_1 = (0, 0, 0)
COLOR_2 = (100, 100, 100)
RED = (255, 0, 0)
YEL = (255, 255, 0)


class Position:
    def __init__(self):
        self.st = np.zeros([6, 7], int)   # state of the board (0 for empty, 1 or -1 for players 1 or -1 respectively)
        self.moves = 0                    # moves played so far
        self.player = 1                   # player currently playing (1 or -1)

    def __repr__(self):
        return repr(self.st[::-1])

    # check whether a column can be played
    def can_play(self, c):
        return self.st[5][c] == 0         # check whether the top square of the column is empty

    # return the first available row of a non-full column
    def get_row(self, c):
        r = 0
        while self.st[r][c] != 0:
            r += 1
        return r

    # play a stone in a given non-full column
    def play(self, c):
        r = self.get_row(c)

        self.st[r][c] = self.player
        self.moves += 1
        self.player *= -1

        return r                          # return the row where the stone is placed

    # play a sequence of moves specified as an input iterable
    def play_sequence(self, seq):
        for move in seq:
            self.play(int(move))

    # restore the state of the board to the previous move (takes as input the coordinates of the last stone placed)
    def undo(self, r, c):
        self.st[r][c] = 0
        self.moves -= 1
        self.player *= -1

    # check whether playing a stone in a given column is winning immediately
    def is_winning(self, c):
        r = self.play(c)

        # check vertical
        if r > 2 and self.st[r][c] == self.st[r-1][c] == self.st[r-2][c] == self.st[r-3][c]:
            self.undo(r, c)
            return True

        # check horizontal
        for i in range(4):
            if 0 <= c-i < 4 and self.st[r][c-i] == self.st[r][c-i+1] == self.st[r][c-i+2] == self.st[r][c-i+3]:
                self.undo(r, c)
                return True

        # check diagonal
        for i in range(4):
            if 0 <= r-i < 3 and 0 <= c-i < 4 and self.st[r-i][c-i] == self.st[r-i+1][c-i+1] == self.st[r-i+2][c-i+2] == self.st[r-i+3][c-i+3]:
                self.undo(r, c)
                return True
            if 0 <= r-i < 3 <= c+i < 7 and self.st[r-i][c+i] == self.st[r-i+1][c+i-1] == self.st[r-i+2][c+i-2] == self.st[r-i+3][c+i-3]:
                self.undo(r, c)
                return True

        self.undo(r, c)
        return False

    def static_eval(self):
        return 0

    # minmax search with alpha-beta pruning
    def negamax(self, d, alpha, beta):

        # check if the position is winnable with one move
        for i in range(7):
            if self.can_play(i) and self.is_winning(i):
                return math.floor((41 - self.moves) / 2)

        # check if the position is drawn
        if self.moves == 41:
            return 0

        # updates the [alpha, beta] window based on the number of moves left, and if it is empty cuts the exploration
        roof = math.floor((41 - self.moves) / 2)
        if beta > roof:
            beta = roof
        if alpha >= beta:
            return beta

        # recursive calls
        if d > 0:
            for i in [3, 2, 4, 1, 5, 0, 6]:
                if self.can_play(i):
                    r = self.play(i)
                    score = - self.negamax(d - 1, - beta, - alpha)
                    self.undo(r, i)
                    if score >= beta:
                        return score
                    if score > alpha:
                        alpha = score
            return alpha
        else:
            return self.static_eval()

    # find the best move in the position
    def search(self):
        for c in range(7):
            if self.can_play(c) and self.is_winning(c):
                return c
        if self.moves == 41:
            for c in range(7):
                if self.can_play(c):
                    return c

        scores = [-21] * 7
        for c in [3, 2, 4, 1, 5, 0, 6]:
            if self.can_play(c):
                r = self.play(c)
                score = - self.negamax(DEPTH, -21, 21)
                self.undo(r, c)
                scores[c] = score
        move = 3
        for c in [2, 4, 1, 5, 0, 6]:
            if scores[c] > scores[move]:
                move = c
        return move


class Game:
    def __init__(self, players=1, ai_begins=False):
        self.pos = Position()        # stores the position on the board
        self.screen = None           # graphic interface
        self.outcome = None          # outcome of the game (0 -> draw; 1 -> player 1 wins; -1 -> player -1 wins)
        self.players = players       # number of players
        self.ai_begins = ai_begins   # indicates whether the AI plays first

    # graphic interface initialization
    def initialize_screen(self):
        pg.init()
        self.screen = pg.display.set_mode(SIZE)

    # draw the board
    def draw_board(self):
        pg.draw.rect(self.screen, COLOR_1, (0, 0, SIZE[0], SIZE[1]))
        for i in range(6):
            for j in range(7):
                pg.draw.rect(self.screen, COLOR_2, (j * SIDE, i * SIDE, SIDE, SIDE), width=4)
                pg.draw.circle(self.screen, COLOR_2, ((j + 0.5) * SIDE, (i + 0.5) * SIDE), RADIUS)
        pg.display.update()

    # update the board after a move
    def draw_move(self, c):
        r = self.pos.get_row(c)

        color = (RED if self.pos.player == 1 else YEL)
        center = ((c + 0.5) * SIDE, (6 - r - 0.5) * SIDE)
        pg.draw.circle(self.screen, color, center, RADIUS)
        pg.display.update()

    # check if the move is playable. If it is, check outcome and update state and interface.
    def make_move(self, c):
        if self.pos.can_play(c):
            if self.pos.is_winning(c):
                self.outcome = self.pos.player
                print("player {0} wins!".format(1 if self.pos.player == 1 else 2))
            elif self.pos.moves == 41:
                self.outcome = 0
                print("draw!")
            self.draw_move(c)
            self.pos.play(c)

    # main cycle
    def main(self):
        self.initialize_screen()
        self.draw_board()

        if self.ai_begins:
            ai_move = self.pos.search()
            self.make_move(ai_move)

        while self.outcome is None:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    c = math.floor(event.pos[0] / SIDE)
                    self.make_move(c)

                    if self.players == 1 and self.outcome is None:
                        ai_move = self.pos.search()
                        self.make_move(ai_move)

                    if self.outcome is not None:
                        time.sleep(5)


if __name__ == '__main__':
    g = Game(1, 1)
    g.main()
