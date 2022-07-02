#Zackary Mimoso
#December 7 2021
#Organization of Programming Languages
#Chess Game Implementation

class GameState:
    def __init__(self):

        self.board = [['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
                      ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
                      ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        # Keeping track of kings to make valid move calculation and castling easier.
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.check = False
        # keep track of checkmate and stalemate
        self.checkMate = False
        self.staleMate = False

        self.enPassantPossible = ()

        # castling
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [
            CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                         self.currentCastlingRights.bks, self.currentCastlingRights.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'  # empty the start cell
        self.board[move.endRow][move.endCol] = move.pieceMoved  # keep the piece moved on the end cell
        self.moveLog.append(move)  # record the move
        # UPDATE KING'S POSITION
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # En-Passant
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--'  # Capturing the Piece

        # Update enPassantPossible Variable
        if move.pieceMoved[1] == 'P' and abs(move.endRow - move.startRow) == 2:  # only on 2 sq. pawn advance
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enPassantPossible = ()

        # castle Move
        if move.isCastleMove:
            if move.endCol < move.startCol:  # Queen side castle
                self.board[move.endRow][0] = '--'
                self.board[move.endRow][move.endCol + 1] = move.pieceMoved[0] + 'R'
            else:  # King side castle
                self.board[move.endRow][7] = '--'
                self.board[move.endRow][move.endCol - 1] = move.pieceMoved[0] + 'R'

        # Update 7. Castling Rights
        self.updateCastlingRights(move)
        newCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                       self.currentCastlingRights.bks, self.currentCastlingRights.bqs)
        self.castleRightsLog.append(newCastleRights)
        self.whiteToMove = not self.whiteToMove  # swap the turn

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved  # put piece on the starting square
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # puts back the captured piece
            self.whiteToMove = not self.whiteToMove  # switch turns

            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            if move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo Enpassant Move
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)

            # UNDO a 2 sq pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.endRow - move.startRow) == 2:
                self.enPassantPossible = ()

            # UNDO castling rights and also tabs if they are able to castle:
            self.castleRightsLog.pop()
            self.currentCastlingRights.wks = self.castleRightsLog[-1].wks
            self.currentCastlingRights.wqs = self.castleRightsLog[-1].wqs
            self.currentCastlingRights.bks = self.castleRightsLog[-1].bks
            self.currentCastlingRights.bqs = self.castleRightsLog[-1].bqs

            # UNDO CASTLING MOVE:
            if move.isCastleMove:
                if move.endCol < move.startCol:  # Queen Side Castle
                    self.board[move.endRow][move.endCol + 1] = '--'
                    self.board[move.endRow][0] = move.pieceMoved[0] + 'R'
                else:  # King side castle
                    self.board[move.endRow][move.endCol - 1] = '--'
                    self.board[move.endRow][7] = move.pieceMoved[0] + 'R'
                    # Set checkmate and stalemate false again
        self.checkMate = False
        self.staleMate = False

    def updateCastlingRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wqs = False
            self.currentCastlingRights.wks = False

        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bqs = False
            self.currentCastlingRights.bks = False

        elif move.pieceMoved == 'wR':
            if move.startRow == 7 and move.startCol == 0:
                self.currentCastlingRights.wqs = False
            if move.startRow == 7 and move.startCol == 7:
                self.currentCastlingRights.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0 and move.startCol == 0:
                self.currentCastlingRights.bqs = False
            if move.startRow == 0 and move.startCol == 7:
                self.currentCastlingRights.bks = False

    def getValidMoves(self):
        moves = []
        tempEnPassant = self.enPassantPossible
        tempCastlingRights = self.currentCastlingRights
        moves = self.getAllPossibleMoves()
        currentKingLocation = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        self.getCastlingMoves(currentKingLocation[0], currentKingLocation[1], moves)
        # make a move from the list of possible moves
        for i in range(len(moves) - 1, -1,
                       -1):  # traversing in opposite direction cause we have to remove some elements from the middle.
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove  # for generating opponent's move change turn
            # Check if any of the opponents move leads to check -> if so remove the move from our list
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        # Return the final list of moves
        if len(moves) == 0:
            if self.inCheck():
                print("CHECK MATE! " + ('white' if not self.whiteToMove else 'black') + " wins")

                self.checkMate = True
            else:
                print("DRAW DUE TO STALEMATE")
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        self.enPassantPossible = tempEnPassant
        self.currentCastlingRights = tempCastlingRights
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.isUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.isUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # Replaces def checkForPinsAndChecks
    def isUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        opponentsMove = self.getAllPossibleMoves()  # generate opponents move
        self.whiteToMove = not self.whiteToMove  # switch back turns
        for move in opponentsMove:
            if move.endRow == r and move.endCol == c:  # sq under attack
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                piece = self.board[r][c][1]
                if not ((self.whiteToMove) ^ (turn == 'w')):
                    if piece != '-':
                        self.moveFunctions[piece](r, c, moves)  # calls the appropriate piece move function
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove and self.board[r][c][0] == 'w':  # WHITE PAWN MOVES
            if self.board[r - 1][c] == '--':  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':  # enemy piece to capture to the left
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                if self.enPassantPossible == (r - 1, c - 1):
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
            if c + 1 < len(self.board):
                if self.board[r - 1][c + 1][0] == 'b':  # enemy piece to capture to the right
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                if self.enPassantPossible == (r - 1, c + 1):
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassantMove=True))

        if not self.whiteToMove and self.board[r][c][0] == 'b':  # BLACK PAWN MOVES
            if self.board[r + 1][c] == '--':  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':  # enemy piece to capture to the left
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                if self.enPassantPossible == (r + 1, c - 1):
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))
            if c + 1 < len(self.board):
                if self.board[r + 1][c + 1][0] == 'w':  # enemy piece to capture to the right
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                if self.enPassantPossible == (r + 1, c + 1):
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))

    def getRookMoves(self, r, c, moves):

        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))  # up down left right
        enemyColor = 'b' if self.whiteToMove else 'w'  # opponent's color according to current turn
        for d in directions:
            for i in range(1, 8):
                endRow = r + (d[0] * i)
                endCol = c + (d[1] * i)
                if endRow >= 0 and endRow < len(self.board) and endCol >= 0 and endCol < len(self.board[endRow]):
                    if self.board[endRow][endCol] == '--':  # Empty Square
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif self.board[endRow][endCol][0] == enemyColor:  # capture opponent's piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break  # same color piece
                else:
                    break  # off board

    def getKnightMoves(self, r, c, moves):
        directions = ((-1, -2), (-2, -1), (1, -2), (2, -1), (1, 2), (2, 1), (-1, 2), (-2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'  # opponent's color according to current turn
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if endRow >= 0 and endRow < len(self.board) and endCol >= 0 and endCol < len(self.board[endRow]):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # (top left) (top right) (bottom left) (bottom right)
        enemyColor = 'b' if self.whiteToMove else 'w'  # opponent's color according to current turn
        for d in directions:
            for i in range(1, 8):
                endRow = r + (d[0] * i)
                endCol = c + (d[1] * i)
                if endRow >= 0 and endRow < len(self.board) and endCol >= 0 and endCol < len(self.board[endRow]):
                    if self.board[endRow][endCol] == '--':  # Empty Square
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif self.board[endRow][endCol][0] == enemyColor:  # capture opponent's piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break  # same color piece
                else:
                    break  # off board

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'  # ally color according to current turn
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if endRow >= 0 and endRow < len(self.board) and endCol >= 0 and endCol < len(self.board[endRow]):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastlingMoves(self, r, c, moves):
        if self.inCheck():
            return "you cant castle! your king is under attack!"

        if (self.whiteToMove and self.currentCastlingRights.wks) or \
                (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r, c, moves)

        if (self.whiteToMove and self.currentCastlingRights.wqs) or \
                (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.isUnderAttack(r, c + 1) and not self.isUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.isUnderAttack(r, c - 1) and not self.isUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights():

    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs

    def __str__(self):
        return ("7. Castling Rights(wk, wq, bk, bq) : " + str(self.wks) + " " + str(self.wqs) + " " + str(
            self.bks) + " " + str(self.bqs))


class Move():
    # maps keys to values
    # creates chess notation for moveLog
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}  # reverses for each of the keys to values
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]  # can't be '--'
        self.pieceCaptured = board[self.endRow][self.endCol]  # can be '--' -> no piece was captured
        # Pawn Promotion
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (
                self.pieceMoved == 'bP' and self.endRow == 7)

        # En Passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        # CastleMove
        self.isCastleMove = isCastleMove

        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def getChessNotation(self):
        return self.getFileRank(self.startRow, self.startCol) + self.getFileRank(self.endRow, self.endCol)

    def getFileRank(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __eq__(self, other):
        return isinstance(other, Move) and self.moveId == other.moveId
