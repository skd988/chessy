EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

HUMAN = 0
RANDOM = 1

LEFT = -1
RIGHT = 1
BLACK: int = -1
WHITE = 1

BOARD_SIZE = 8

GAME_NOT_ENDED = 0
WIN = 1
STALEMATE = 1
INSUFFICIENT_MATERIAL = 2
REPETITION = 3
FIFTY_MOVES = 4

HALF_MOVES_MAX = 50

PIECE_SETUP = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
PIECE_TO_CHARS = {EMPTY: ' ', PAWN: 'p', KNIGHT: 'n', BISHOP: 'b', ROOK: 'r', QUEEN: 'q', KING: 'k'}
CHAR_TO_PIECES = {char: piece for piece, char in PIECE_TO_CHARS.items()}
PIECE_CHAR_BLACK_TO_WHITE = -32

PROMOTION_INPUT = {'n': KNIGHT, 'b': BISHOP, 'r': ROOK, 'q': QUEEN}
PLAYER_NAMES = {BLACK: "Black", WHITE: "White"}
BISHOP_DIRECTIONS = ((-1, -1), (-1, 1), (1, -1), (1, 1))
ROOK_DIRECTIONS = ((-1, 0), (1, 0), (0, 1), (0, -1))
KING_QUEEN_DIRECTIONS = ROOK_DIRECTIONS + BISHOP_DIRECTIONS
KNIGHT_DIRECTIONS = ((-2, 1), (-2, -1), (2, 1), (2, -1), (-1, 2), (-1, -2), (1, 2), (1, -2))
ALL_DIRECTIONS = KING_QUEEN_DIRECTIONS + KNIGHT_DIRECTIONS
PAWN_TAKING_DIRECTION = {BLACK: ((-1, -1), (-1, 1)), WHITE: ((1, -1), (1, 1))}
KING_STARTING_POSITION = {BLACK: (BOARD_SIZE - 1, BOARD_SIZE // 2), WHITE: (0, BOARD_SIZE // 2)}
CASTLING_POSITIONS = {BLACK: {LEFT: (BOARD_SIZE - 1, BOARD_SIZE // 2 - 2),
                              RIGHT: (BOARD_SIZE - 1, BOARD_SIZE // 2 + 2)},
                      WHITE: {LEFT: (0, BOARD_SIZE // 2 - 2),
                              RIGHT: (0, BOARD_SIZE // 2 + 2)}}
ROOK_STARTING_POSITION = {BLACK: {LEFT: (BOARD_SIZE - 1, 0),
                                  RIGHT: (BOARD_SIZE - 1, BOARD_SIZE - 1)},
                          WHITE: {LEFT: (0, 0),
                                  RIGHT: (0, BOARD_SIZE - 1)}}
DIRECTIONS = {KNIGHT: KNIGHT_DIRECTIONS,
              BISHOP: BISHOP_DIRECTIONS, ROOK: ROOK_DIRECTIONS,
              QUEEN: KING_QUEEN_DIRECTIONS, KING: KING_QUEEN_DIRECTIONS}
PAWN_ROW = {BLACK: BOARD_SIZE - 2, WHITE: 1}
PIECE_ROW = {BLACK: BOARD_SIZE - 1, WHITE: 0}
PIECES_NAMES = {PAWN: "Pawn", KNIGHT: "Knight", BISHOP: "Bishop", ROOK: "Rook", QUEEN: "Queen", KING: "King"}


def sign(num):
    return 0 if num == 0 else 1 if num > 0 else -1


def add2DVectors(v1, v2):
    return v1[0] + v2[0], v1[1] + v2[1]


def sub2DVectors(v1, v2):
    return v1[0] - v2[0], v1[1] - v2[1]


def parseMove(move):
    move = move.replace(' ', '')
    if len(move) != 4 or not move[1].isnumeric() or not move[3].isnumeric():
        return None

    move = (chessCoordinatesToLoc(move[0:2]), chessCoordinatesToLoc(move[2:4]))
    return move if all([0 <= c < BOARD_SIZE for co in move for c in co]) else None


def chessCoordinatesToLoc(coord):
    return int(coord[1]) - 1, ord(coord[0]) - ord('a')

def locToChessCoordinates(loc):
    return chr(loc[1] + ord('a')) + str(loc[0] + 1)


def moveToChessCoordinates(start, dest):
    return locToChessCoordinates(start) + locToChessCoordinates(dest)
