#Zackary Mimoso
#December 7 2021
#Organization of Programming Languages
#Chess Game Implementation

import pygame as p
import ChessEngine
import RandomBot

p.init()

BOARD_WIDTH = BOARD_HEIGHT = 480
MOVE_LOG_PANNEL_WIDTH = 200
MOVE_LOG_PANNEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # 8*8 CHESS BOARD
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
MOVE_LOG_FONT = p.font.SysFont('Arial', 12, False, False)


def loadImages():
    pieces = ['bP', 'bR', 'bN', 'bB', 'bQ', 'bK', 'wP', 'wR', 'wN', 'wB', 'wQ', 'wK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANNEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()  # get a list of valid moves.
    moveMade = False  # to check if the user made a move. If true recalculate validMoves.
    loadImages()  # only do this once -> before the while loop
    running = True
    sqSelected = ()  # no sq is selected initially, keep track of the last click by the user -> (tuple : (row,col))
    playerClicks = []  # Logs player clicks
    playerOne = True  # if Human is playing white -> this will be true
    playerTwo = True # if Human is playing black -> this will be true
    gameOver = False  # True in case of Checkmate and Stalemate
    UndoCheck = False  # This fix the bug to make sure player undo's the move made first and then it will be the bot's
    # turn
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # MOUSE HANDLERS
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) position of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    # ``` Quality of Life Features ```
                    # `````````````````````````````````
                    if (col >= 8):  # Click out of board (on move log panel) -> do nothing
                        continue
                    if sqSelected == (row, col):  # user selected the same sq. twice -> deselect the selecion
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both 1st and 2nd click
                        if len(playerClicks) == 2:  # when 2nd click
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i])
                                    moveMade = True
                                    playerClicks = []  # reset playerClicks
                                    sqSelected = ()  # reset user clicks
                                    UndoCheck = False
                            if not moveMade:
                                playerClicks = [sqSelected]

            # KEY HANDLERS
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo last move id 'z' is pressed
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    gameOver = False
                    moveMade = True
                    UndoCheck = True
                if e.key == p.K_r:  # reset the game if 'r' is pressed
                    gs = ChessEngine.GameState()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    validMoves = gs.getValidMoves()

        # AI Move finder logic
        if not gameOver and not humanTurn and UndoCheck == False:
            AIMove = RandomBot.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
        elif not gameOver and not humanTurn and UndoCheck == True:
            moveMade = True
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs, sqSelected, validMoves)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, "Black Won by Checkmate!");
            else:
                drawEndGameText(screen, "White Won by Checkmate!");

        if gs.staleMate:
            gameOver = True
            drawEndGameText(screen, "Draw due to Stalemate!");
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, selectedSquare, validMoves):
    drawBoard(screen)  # draw squares on board (should be called before drawing anything else)
    highlightSquares(screen, gs, selectedSquare, validMoves)
    if len(gs.moveLog) > 0:
        highlightLastMove(screen, gs.moveLog[-1])
    drawPieces(screen, gs.board)  # draw pieces on the board
    drawMoveLog(screen, gs)


def drawBoard(screen):
    global colors
    colors = [p.Color(255, 255, 255), p.Color(25, 30, 100)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(SQ_SIZE * c, SQ_SIZE * r, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, selectedSquare, validMoves):
    if selectedSquare != ():
        r, c = selectedSquare
        enemyColor = 'b' if gs.whiteToMove else 'w'
        allyColor = 'w' if gs.whiteToMove else 'b'
        if gs.board[r][c][0] == allyColor:
            # Highlighting the selected Square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 : 100% transparent | 255 : 100% Opaque
            # Highlighting the valid move squares
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    endRow = move.endRow
                    endCol = move.endCol
                    if gs.board[endRow][endCol] == '--' or gs.board[endRow][endCol][0] == enemyColor:
                        screen.blit(s, (endCol * SQ_SIZE, endRow * SQ_SIZE))


def highlightLastMove(screen, move):
    startRow = move.startRow
    startCol = move.startCol
    endRow = move.endRow
    endCol = move.endCol
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.fill(p.Color("red"))
    screen.blit(s, (startCol * SQ_SIZE, startRow * SQ_SIZE))
    screen.blit(s, (endCol * SQ_SIZE, endRow * SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(SQ_SIZE * c, SQ_SIZE * r, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs):
    font = MOVE_LOG_FONT
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANNEL_WIDTH, MOVE_LOG_PANNEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), moveLogRect)
    moveLog = []
    for i in range(0, len(gs.moveLog), 2):
        moveText = str(i // 2 + 1) + ".  " + gs.moveLog[i].getChessNotation()
        if i < len(gs.moveLog) - 1:
            moveText += "   " + gs.moveLog[i + 1].getChessNotation()
        moveLog.append(moveText)

    horizontalPadding = 5
    verticalPadding = 5
    lineSpacing = 5
    for i in range(len(moveLog)):
        textObject = font.render(moveLog[i], True, p.Color('white'))
        if (verticalPadding + textObject.get_height() >= (MOVE_LOG_PANNEL_HEIGHT - 1)):
            verticalPadding = 10
            horizontalPadding += 100
        textLocation = p.Rect(moveLogRect.move(horizontalPadding, verticalPadding))
        verticalPadding += textObject.get_height() + lineSpacing

        screen.blit(textObject, textLocation)


def drawEndGameText(screen, text):
    #  Font Name  Size Bold  Italics
    font = p.font.SysFont('Helvitica', 32, True, False)
    textObject = font.render(text, 0, p.Color('White'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))
    textObject = font.render(text, 0, p.Color('red'))
    screen.blit(textObject, textLocation.move(4, 4))


if __name__ == '__main__':
    main()
