from util import *
import time
import random


class Tui:
    def __init__(self, display_view=WHITE):
        self.display_view = display_view

    def inputMove(self, board, player):
        move = None
        while move is None:
            move = parseMove(input("Enter your move: "))

        return move

    def inputPromotion(self):
        promo = None
        while promo not in PROMOTION_INPUT.keys():
            promo = input("Choose piece promotion (n, b, r, q): ").lower()

        return PROMOTION_INPUT[promo]

    def displayBoard(self, board, player):
        print(PLAYER_NAMES[player] + ' to play')

        counter = BOARD_SIZE if self.display_view == WHITE else 1
        print_board = board[:]
        if self.display_view == WHITE:
            print_board.reverse()
        for row in print_board:
            print(counter, '| ', end='')
            counter -= self.display_view
            for col in row:
                to_print = PIECE_TO_CHARS[abs(col)]
                if col > 0:
                    to_print = chr(ord(to_print) + PIECE_CHAR_BLACK_TO_WHITE)
                print(to_print, '| ', end='')
            print()

        print(' ', end='')
        for i in range(BOARD_SIZE):
            print('   ', chr(ord('a') + i), sep='', end='')
        print()
