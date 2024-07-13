import pygame
from util import *
import os

WHITE_TILES_COLOR = (51, 87, 255)
BLACK_TILES_COLOR = (220, 20, 60)

PICTURES_FORMAT = ".png"
PICTURES_DIR = "pieces"

TILE_SIZE = 60


class Gui:
    def __init__(self, display_view=WHITE):
        pygame.init()
        self.screen = pygame.display.set_mode((TILE_SIZE * BOARD_SIZE, TILE_SIZE * BOARD_SIZE))
        pygame.display.set_caption('Chess')
        self.tiles = []
        self.pictures = {BLACK: {}, WHITE: {}}
        self.display_view = display_view
        for row in range(BOARD_SIZE):
            self.tiles.append([])
            for col in range(BOARD_SIZE):
                self.tiles[row].append(pygame.Rect(TILE_SIZE * col, TILE_SIZE * row, TILE_SIZE, TILE_SIZE))
        self.loadPictures()

    def displayBoard(self, board, player):
        for row in range(BOARD_SIZE):
            row_to_print = BOARD_SIZE - row - 1 if self.display_view == WHITE else row
            for col in range(BOARD_SIZE):
                pygame.draw.rect(self.screen, WHITE_TILES_COLOR if (row_to_print + col) % 2 == 0 else BLACK_TILES_COLOR,
                                 self.tiles[row_to_print][col])
                content = board[row][col]
                if content != EMPTY:
                    self.screen.blit(self.pictures[sign(content)][abs(content)],
                                     (col * TILE_SIZE,
                                      row_to_print * TILE_SIZE))

        pygame.display.update()

    def inputMove(self, board, player):
        src, dest = None, None
        while src is None:
            src = self.getMouseBoardPosition()
            if sign(board[src[0]][src[1]]) != player:
                src = None

        while dest is None:
            print(src)
            dest = self.getMouseBoardPosition()
            if sign(board[dest[0]][dest[1]]) == player:
                src = dest
                dest = None

        return src, dest

    def getMouseBoardPosition(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    return (BOARD_SIZE - 1 - pos[1] // TILE_SIZE if self.display_view == WHITE
                            else pos[1] // TILE_SIZE, pos[0] // TILE_SIZE)

    def inputPromotion(self):
        promo = None
        while promo not in PROMOTION_INPUT.keys():
            promo = input("Choose piece promotion (n, b, r, q): ").lower()

        return PROMOTION_INPUT[promo]

    def loadPiecePicture(self, content):
        path = os.path.join(PICTURES_DIR,
                            PLAYER_NAMES[sign(content)] + "_" + PIECES_NAMES[abs(content)] + PICTURES_FORMAT)
        path = path.lower()
        picture = pygame.image.load(path)
        picture = pygame.transform.scale(picture, (TILE_SIZE, TILE_SIZE))
        self.pictures[sign(content)][abs(content)] = picture

    def loadPictures(self):
        for player in PLAYER_NAMES.keys():
            for piece in PIECES_NAMES.keys():
                self.loadPiecePicture(player * piece)