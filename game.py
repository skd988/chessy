import random
import time
from util import *
from tui import Tui
from gui import Gui


def betweenOrEqual(a, b, check):
    a, b = (a, b) if a < b else (b, a)
    return a <= check <= b


def createEmptyBoard():
    return [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]


def createStarterBoard():
    board = createEmptyBoard()
    board[0] = PIECE_SETUP
    board[BOARD_SIZE - 1] = [-p for p in PIECE_SETUP]
    board[1] = [1] * BOARD_SIZE
    board[BOARD_SIZE - 2] = [-1] * BOARD_SIZE
    return board


def isInBetween(loc, start, end):
    distance = sub2DVectors(end, start)
    if loc == start or loc == end:
        return True

    if distance[0] != 0 and distance[1] != 0 and abs(distance[0]) != abs(distance[1]):
        return False

    direction = tuple([sign(n) for n in distance])
    distance_from_loc = sub2DVectors(end, loc)
    if distance_from_loc[0] != 0 and distance_from_loc[1] != 0 and \
            abs(distance_from_loc[0]) != abs(distance_from_loc[1]):
        return False

    direction_loc = tuple([sign(n) for n in distance_from_loc])

    return direction == direction_loc and \
        betweenOrEqual(start[0], end[0], loc[0]) and betweenOrEqual(start[1], end[1], loc[1])


class Game:
    def __init__(self, moves=None, fen=None, gui=True, black=RANDOM, white=HUMAN):
        if moves is None:
            moves = []
        self.players = {BLACK: black, WHITE: white}
        self.moves = []
        self.movesToMake = moves
        self.pins = {}
        self.threatsOnKing = []
        if fen is None:
            self.fullMoves = 0
            self.board = createStarterBoard()
            self.piecesAndMoves = {BLACK: {(i, j): [] for i in [BOARD_SIZE - 1, BOARD_SIZE - 2]
                                           for j in range(0, BOARD_SIZE)},
                                   WHITE: {(i, j): [] for i in [0, 1] for j in range(0, BOARD_SIZE)}}
            self.castlingRights = {BLACK: {LEFT: True, RIGHT: True}, WHITE: {LEFT: True, RIGHT: True}}
            self.enPassant = None
            self.player = WHITE
            self.halfMoves = 0
            self.kingsLocation = KING_STARTING_POSITION.copy()
        else:
            if not self.loadFen(fen):
                raise "Fen is invalid"

        display_view = WHITE if white == HUMAN else BLACK
        self.user_interface = Gui(display_view) if gui else Tui(display_view)

    def play(self):
        src, dest = None, None
        is_promotion = False

        while True:
            print("FEN:", self.getFen())
            self.findPossibleMoves()
            self.user_interface.displayBoard(self.board, self.player)
            self.printPossibleMoves()
            status = self.gameEndedStatus()
            if status != GAME_NOT_ENDED:
                break
            move_made = False
            while not move_made:
                src, dest = self.getMove()
                move_made, is_promotion = self.makeMove(src, dest)
            if is_promotion:
                promotion = self.getPromotion()
                self.promote(dest, promotion)

            self.moves.append((src, dest))
            self.player *= -1

        if status == WIN:
            print(PLAYER_NAMES[-self.player], 'Won!')
        else:
            print('It\'s a tie!')

    def getMove(self):
        if len(self.movesToMake) > 0:
            move = parseMove(self.movesToMake.pop())

        elif self.players[self.player] == RANDOM:
            print('thinking...')
            time.sleep(1)
            move = random.choice(self.getMoveList())
            print('My move is', move)
        else:
            move = self.user_interface.inputMove(self.board, self.player)

        return move

    def getPromotion(self):
        if self.players[self.player] != HUMAN:
            return random.choice(list(PROMOTION_INPUT.values()))

        return self.user_interface.inputPromotion()

    def promote(self, dest, promotion):
        self.set(dest, promotion * self.player)

    def getMoveList(self):
        return [(src, dest) for src in self.piecesAndMoves[self.player].keys()
                for dest in self.piecesAndMoves[self.player][src]]

    def gameEndedStatus(self):
        if not self.hasMoves():
            return WIN if self.isInCheck() else STALEMATE
        if self.halfMoves == HALF_MOVES_MAX:
            return FIFTY_MOVES
        # add repetition and insufficient
        return GAME_NOT_ENDED

    def hasMoves(self):
        return sum([len(moves) for moves in self.piecesAndMoves[self.player].values()]) > 0

    def printPossibleMoves(self):
        for src, moves in self.piecesAndMoves[self.player].items():
            if len(moves) == 0:
                continue
            print(locToChessCoordinates(src) + ': ', end='')

            for dest in moves:
                print(locToChessCoordinates(dest), end=' ')
            print('\t', end='')
        print()
        print()

    def makeMove(self, src, dest):
        if src not in self.piecesAndMoves[self.player] \
                or dest not in self.piecesAndMoves[self.player][src]:
            return False, False

        promotion = False

        self.halfMoves += 1
        if self.player == BLACK:
            self.fullMoves += 1

        src_content = self.get(src)
        src_piece = abs(src_content)
        dest_content = self.get(dest)
        if src_piece == KING:
            self.kingsLocation[self.player] = dest
            difference = dest[1] - src[1]
            if abs(difference) == 2:
                side = sign(difference)
                self.changePieceLoc(ROOK_STARTING_POSITION[self.player][side], add2DVectors(dest, (0, -side)))

            for side in (LEFT, RIGHT):
                self.castlingRights[self.player][side] = False

        elif src_piece == ROOK:
            for side in (LEFT, RIGHT):
                if src == ROOK_STARTING_POSITION[self.player][side]:
                    self.castlingRights[self.player][side] = False

        if dest_content * self.player < 0:
            self.piecesAndMoves[-self.player].pop(dest)
            self.halfMoves = 0

        self.changePieceLoc(src, dest)
        if src_piece == PAWN:
            self.halfMoves = 0
            promotion = dest[0] == PIECE_ROW[-self.player]
            if dest == self.enPassant:
                self.set((dest[0] - self.player, dest[1]), EMPTY)

        self.enPassant = (src[0] + self.player, src[1]) if src_piece == PAWN and abs(dest[0] - src[0]) == 2 else None
        return True, promotion

    def changePieceLoc(self, src, dest):
        self.set(dest, self.get(src))
        self.set(src, EMPTY)

    def findPossibleMoves(self):
        king_loc = self.kingsLocation[self.player]
        self.threatsOnKing, self.pins = self.findThreats(king_loc, True)
        if self.isInCheck():
            pass
        for loc in self.piecesAndMoves[self.player]:
            self.findMoves(loc)

    def searchPieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                content = self.get((row, col))
                if self.board[row][col] != EMPTY:
                    player = sign(content)
                    self.piecesAndMoves[player][(row, col)] = []
                    if abs(content) == KING:
                        self.kingsLocation[player] = (row, col)

    def findMoves(self, src):
        piece = self.get(src) * self.player
        # content will be <= 0 if loc contains an enemy piece or empty
        if piece <= 0:
            return

        self.piecesAndMoves[self.player][src] = []

        # double check? don't even bother
        if piece != KING and len(self.threatsOnKing) > 1:
            return

        if piece == PAWN:
            dest = (src[0] + self.player, src[1])
            if self.isMoveValidPawnAdvance(src, dest):
                self.addMove(src, dest)

            if src[0] == PAWN_ROW[self.player] and self.get(dest) == EMPTY:
                dest = (dest[0] + self.player, dest[1])
                if self.isMoveValidPawnAdvance(src, dest):
                    self.addMove(src, dest)

            for direction in PAWN_TAKING_DIRECTION[self.player]:
                dest = add2DVectors(src, direction)
                if self.isMoveValidPawnTake(src, dest):
                    self.addMove(src, dest)
            return

        is_one_step = piece == KING or piece == KNIGHT
        for direction in DIRECTIONS[piece]:
            dest = add2DVectors(src, direction)
            while self.isInBoard(dest):
                if self.isMoveValid(src, dest, piece):
                    self.addMove(src, dest)

                if is_one_step or self.get(dest) != EMPTY:
                    break

                dest = add2DVectors(dest, direction)

        if piece == KING:
            if not self.isInCheck():
                for side in (LEFT, RIGHT):
                    if self.isCastlingSideAvailable(side):
                        self.addMove(src, CASTLING_POSITIONS[self.player][side])

    def isCastlingSideAvailable(self, side):
        middle_tile = add2DVectors(KING_STARTING_POSITION[self.player], (0, side))
        return self.castlingRights[self.player][side] \
            and middle_tile in self.piecesAndMoves[self.player][KING_STARTING_POSITION[self.player]] \
            and self.get(middle_tile) == 0 \
            and self.isThreatened(CASTLING_POSITIONS[self.player][side]) \
            and self.get(CASTLING_POSITIONS[self.player][side]) == 0

    def isInCheck(self):
        return len(self.threatsOnKing) != 0

    def addMove(self, src, dest):
        self.piecesAndMoves[self.player][src].append(dest[:])

    def isMoveValidPawnAdvance(self, src, dest):
        return self.get(dest) == EMPTY and self.isKingNotThreatenedAfterMove(src, dest, PAWN)

    def isMoveValidPawnTake(self, src, dest):
        return self.isInBoard(dest) and (self.get(dest) * self.player < 0 or dest == self.enPassant) \
            and self.isKingNotThreatenedAfterMove(src, dest, PAWN)

    def isMoveValid(self, src, dest, piece):
        return self.isValidDest(dest) and self.isKingNotThreatenedAfterMove(src, dest, piece)

    def isValidDest(self, dest):
        return self.isInBoard(dest) and not self.isOccupiedByPlayer(dest)

    def isKingNotThreatenedAfterMove(self, src, dest, piece):
        if piece == KING:
            return self.isThreatened(dest)

        # already checked for double check, so if king is checked there's only one trouble
        return (src not in self.pins or isInBetween(dest, self.pins[src], self.kingsLocation[self.player])) \
            and (not self.isInCheck() or isInBetween(dest, self.threatsOnKing[0], self.kingsLocation[self.player]))

    def getFen(self):
        fen = ''
        reverse_board = self.board[:]
        reverse_board.reverse()
        for row in reverse_board:
            empty_tiles = 0
            for tile in row:
                if tile == EMPTY:
                    empty_tiles += 1
                else:
                    if empty_tiles > 0:
                        fen += str(empty_tiles)
                        empty_tiles = 0
                    piece_char = PIECE_TO_CHARS[abs(tile)]
                    fen += piece_char.capitalize() if sign(tile) == WHITE else piece_char
            if empty_tiles > 0:
                fen += str(empty_tiles)
            fen += '/'
        fen = fen[:-1]
        fen += ' '
        fen += 'w' if self.player == WHITE else 'b'
        fen += ' '
        fen += 'K' if self.castlingRights[WHITE][RIGHT] else ''
        fen += 'Q' if self.castlingRights[WHITE][LEFT] else ''
        fen += 'k' if self.castlingRights[BLACK][RIGHT] else ''
        fen += 'q' if self.castlingRights[BLACK][LEFT] else ''
        if fen[-1] == ' ':
            fen += '-'
        fen += ' '
        fen += locToChessCoordinates(self.enPassant) if self.enPassant is not None else '-'
        fen += ' '
        fen += str(self.halfMoves)
        fen += ' '
        fen += str(self.fullMoves)
        return fen

    def loadFen(self, fen):
        rows = fen.split('/')
        rest = rows[-1].split(' ')
        rows[-1] = rest[0]
        rest.pop(0)
        if len(rows) != BOARD_SIZE:
            return False
        self.board = []
        for row in rows:
            tiles = []
            for val in row:
                if val.isnumeric():
                    empty_tiles = int(val)
                    tiles += [EMPTY] * empty_tiles
                else:
                    piece = CHAR_TO_PIECES[val.lower()]
                    if not val.isupper():
                        piece *= -1
                    tiles += [piece]
            self.board.append(tiles)
            if len(tiles) != BOARD_SIZE:
                return False

        if rest[0] == 'w':
            self.player = WHITE
        elif rest[0] == 'b':
            self.player = BLACK
        else:
            return False

        self.board.reverse()
        self.castlingRights = {BLACK: {LEFT: False, RIGHT: False}, WHITE: {LEFT: False, RIGHT: False}}

        if rest[1] == '-':
            pass
        else:
            for char in rest[1]:
                if char == 'K':
                    self.castlingRights[WHITE][RIGHT] = True
                elif char == 'Q':
                    self.castlingRights[WHITE][LEFT] = True
                elif char == 'k':
                    self.castlingRights[BLACK][RIGHT] = True
                elif char == 'q':
                    self.castlingRights[BLACK][LEFT] = True
                else:
                    return False

        if rest[2] == '-':
            self.enPassant = None
        elif len(rest[2]) == 2:
            self.enPassant = chessCoordinatesToLoc(rest[2])
            if not self.isInBoard(self.enPassant):
                return False
        else:
            return False

        if rest[3].isnumeric():
            self.halfMoves = int(rest[3])
        else:
            return False

        if rest[4].isnumeric():
            self.fullMoves = int(rest[4])
        else:
            return False

        self.kingsLocation = {BLACK: None, WHITE: None}
        self.piecesAndMoves = {BLACK: {}, WHITE: {}}
        self.searchPieces()
        if self.kingsLocation[WHITE] is None or self.kingsLocation[BLACK] is None:
            return False

        return True

    def isOccupiedByPlayer(self, loc):
        return self.get(loc) * self.player > 0

    def isThreatened(self, loc):
        return len(self.findThreats(loc)) == 0

    def findThreats(self, loc, findAllAndPins=False):
        threats = []
        pins = {}

        for direction in ALL_DIRECTIONS:
            threat, pinned = self.findThreatDirection(loc, direction, findAllAndPins)
            if threat is not None:
                if pinned is not None:
                    pins[pinned] = threat
                else:
                    threats.append(threat)
                    if not findAllAndPins:
                        return threats

        if findAllAndPins:
            return threats, pins

        return threats

    def findThreatDirection(self, loc, direction, findPin=False):
        loc_check = add2DVectors(loc, direction)
        pinned = None
        first_step = True
        knight_move = direction in KNIGHT_DIRECTIONS
        while self.isInBoard(loc_check) and (first_step or not knight_move):
            content = self.get(loc_check)
            piece = abs(content)
            if content == EMPTY or loc_check == self.kingsLocation[self.player]:
                first_step = False
                loc_check = add2DVectors(loc_check, direction)
                continue
            elif content * self.player > 0:
                if findPin and pinned is None:
                    pinned = loc_check
                else:
                    break
            else:
                if piece == PAWN:
                    if first_step and direction in PAWN_TAKING_DIRECTION[self.player]:
                        return loc_check, pinned
                elif piece == KING:
                    if first_step and direction in DIRECTIONS[piece]:
                        return loc_check, pinned
                elif direction in DIRECTIONS[piece]:
                    return loc_check, pinned

                break

            first_step = False
            loc_check = add2DVectors(loc_check, direction)

        return None, None

    def get(self, loc):
        return self.board[int(loc[0])][int(loc[1])] if self.isInBoard(loc) else None

    def set(self, loc, content):
        if not self.isInBoard(loc):
            return False

        prev_content = self.get(loc)
        self.board[loc[0]][loc[1]] = content
        if prev_content != EMPTY and loc in self.piecesAndMoves[sign(prev_content)]:
            self.piecesAndMoves[sign(prev_content)].pop(loc)
        if content != EMPTY:
            self.piecesAndMoves[sign(content)][loc] = []

        return True

    def isInBoard(self, loc):
        return 0 <= loc[0] < len(self.board) and 0 <= loc[1] < len(self.board[0])
