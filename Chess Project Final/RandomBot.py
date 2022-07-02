#Zackary Mimoso
#December 7 2021
#Organization of Programming Languages
#Chess Game Implementation

import random
import ChessEngine


def findRandomMove(validMoves):
    gs = ChessEngine.GameState()
    Log = gs.moveLog #Possible future implementation for restoring a bot's move if you undo an action
    return validMoves[random.randint(0, len(validMoves) - 1)]
