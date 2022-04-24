import pygame as p
from pygame import *
import ChessEngine
import SmartMoveFinder
import os
import time
from multiprocessing import Process, Queue


def loadImages():
    pieces = ['wp', 'wR', 'wR', 'wN', 'wN', 'wB', 'wK',
              'wQ', 'bp', 'bR', 'bR', 'bN', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load('C:\\Users\\prana\\OneDrive\Documents\\Python Scripts\\Chess-Final\\Images\\' + piece + '.png'), (SQ_SIZE, SQ_SIZE))


"""
make file loading work with any os in any location
"""


def main():
    p.init()
    screen = p.display.set_mode(
        (WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT + MENU_PANEL_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    menuFont = p.font.SysFont("Calibri", 60, False, False)
    menuSFont = p.font.SysFont("Calibri", 20, False, False)
    menuMFont = p.font.SysFont("Calibri", 40, False, False)

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    CheckV = False
    CheckM = False
    soundefon = True
    playerOne = True
    playerTwo = False
    AIThinking = False
    moveFinderProcess = None
    while running:
        humanTurn = (gs.whitetoMove and playerOne) or (
            not gs.whitetoMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col) or col >= 8 or row >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = ChessEngine.Move(
                            playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                soundef = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    if len(gs.moveLog) >= 2:
                        gs.undoMove()
                        gs.undoMove()
                        moveMade = True
                        animate = False
                        checkMate = False
                        staleMate = False
                        gameOver = False
                        soundef = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    checkMate = False
                    staleMate = False
                    gameOver = False
                    soundef = False
                if e.key == p.K_s:
                    if soundefon == True:
                        soundefon = False
                    else:
                        soundefon = True
                if len(gs.moveLog) == 0:
                    if e.key == p.K_1:
                        if playerOne == True:
                            playerOne = False
                        elif playerOne == False:
                            playerOne = True
                    if e.key == p.K_2:
                        if playerTwo == True:
                            playerTwo = False
                        if playerTwo == False:
                            playerTwo = True
        if not gameOver and not humanTurn:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()
                moveFinderProcess = Process(
                    target=SmartMoveFinder.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                soundef = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()


            if gs.inCheck():
                CheckV = True

            if gs.checkMate:
                CheckM = True

            if CheckV == True:
                CheckV = False
                os.system("say 'check'")

            if CheckM == True:
                CheckM = False
                os.system("say 'mate'")

            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves,
                      sqSelected, moveLogFont, menuFont, menuSFont, menuMFont)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            drawEndGameText(
                screen, 'Stalemate' if gs.staleMate else 'Black wins by Checkmate' if gs.whitetoMove else 'White wins by Checkmate')

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, menuFont, smallFont, mediumFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)
    drawMenu(screen, gs, menuFont, smallFont, mediumFont)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whitetoMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i+1]) + " "
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


def drawMenu(screen, gs, font, smallFont, mediumFont):
    menuRect = p.Rect(0, HEIGHT,
                      MENU_PANEL_WIDTH, MENU_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('light blue'), menuRect)
    text = "MENU"
    textob = font.render(text, True, p.Color('Black'))
    screen.blit(textob, (0, HEIGHT))

    SeffectBT = p.Rect(10, HEIGHT + 50, 60, 40)
    SeffectBF = p.Rect(70, HEIGHT + 50, 60, 40)
    p.draw.rect(screen, p.Color('green'), SeffectBT)
    p.draw.rect(screen, p.Color('red'), SeffectBF)
    text2 = "Sound Effects"
    textob2 = smallFont.render(text2, True, p.Color('Black'))
    screen.blit(textob2, (25, HEIGHT + 95))

    text3 = "ON"
    textob3 = mediumFont.render(text3, True, p.Color('Black'))
    screen.blit(textob3, (20, HEIGHT + 55))

    text4 = "OFF"
    textob4 = mediumFont.render(text4, True, p.Color('Black'))
    screen.blit(textob4, (73, HEIGHT + 55))


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        p.event.pump()
        r, c = (move.startRow + dR * frame / frameCount,
                move.startCol + dC*frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE,
                           move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + \
                    1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol*SQ_SIZE,
                                   enPassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(
            c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0,  p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == '__main__':
    WIDTH = HEIGHT = 512
    MOVE_LOG_PANEL_WIDTH = 250
    MOVE_LOG_PANEL_HEIGHT = HEIGHT
    MENU_PANEL_WIDTH = WIDTH + MOVE_LOG_PANEL_WIDTH
    MENU_PANEL_HEIGHT = 250
    DIMENSION = 8
    SQ_SIZE = HEIGHT // DIMENSION
    MAX_FPS = 15
    IMAGES = {}
    main()
