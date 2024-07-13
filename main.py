from game import Game
from util import *
import random

def play():
    moves = []
    fen = None#'3rk2r/pp5p/4b1pP/4p3/4p1p1/bq2P3/1B3PP1/R1K1R3 b k - 3 28'#None#'3r4/pp6/2nQ4/6pk/1Pb1q3/2P1P3/P5RP/7K w - - 1 33'
    human_player = random.choice([BLACK, WHITE])
    game = Game(fen=fen, black=HUMAN if human_player == BLACK else RANDOM,
                white=RANDOM if human_player == BLACK else HUMAN)
    game = Game(fen=fen, black=HUMAN, white=RANDOM)

    game.play()


def main():
    play()


if __name__ == '__main__':
    main()
