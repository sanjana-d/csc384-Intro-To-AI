###############################################################################
# This file contains helper functions and the heuristic functions
# for our AI agents to play the Mancala game.
#
# CSC 384 Fall 2023 Assignment 2
# version 1.0
###############################################################################

import sys

###############################################################################
### DO NOT MODIFY THE CODE BELOW

### Global Constants ###
TOP = 0
BOTTOM = 1

### Errors ###
class InvalidMoveError(RuntimeError):
    pass

class AiTimeoutError(RuntimeError):
    pass

### Functions ###
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_opponent(player):
    if player == BOTTOM:
        return TOP
    return BOTTOM

### DO NOT MODIFY THE CODE ABOVE
###############################################################################


def heuristic_basic(board, player):
    """
    Compute the heuristic value of the current board for the current player 
    based on the basic heuristic function.

    :param board: the current board.
    :param player: the current player.
    :return: an estimated utility of the current board for the current player.
    """
    if board.mancalas is None:
        return 0
    if player is TOP:
        return board.mancalas[TOP] - board.mancalas[BOTTOM]
    else:
        return board.mancalas[BOTTOM] - board.mancalas[TOP]

def heuristic_advanced(board, player): 
    """
    Compute the heuristic value of the current board for the current player
    based on the advanced heuristic function.

    :param board: the current board object.
    :param player: the current player.
    :return: an estimated heuristic value of the current board for the current player.
    """
    total_value = 0
    possible_captures = 0
    moves = board.get_possible_moves(player)
    side = player

    for move in moves:
        new_board = []
        for row in board.pockets: 
            new_board.append(list(row[:]))
        new_mancalas = [board.mancalas[TOP], board.mancalas[BOTTOM]]

        stone_count = board.pockets[side][move] # find the number of stones in the pocket
        new_board[side][move] = 0 # set to 0

        if (player == BOTTOM):
            direction = True
            ind = move + 1
        else:
            direction = False
            ind = move - 1

        while stone_count > 0: #deposit stones around the board
            # we are at the end of the board
            if ind > (len(board.pockets[side])-1) or ind < 0:
                # swap side and change direction
                side = TOP if side == BOTTOM else BOTTOM 
                direction = not direction 

                #if we are at the end of the board, 
                #deposit stone in a mancala before we continue
                if ind > (len(board.pockets[side]) - 1): 
                    if player == BOTTOM:
                        stone_count -= 1
                        new_mancalas[player] += 1
                    ind = len(board.pockets[side])-1
                else:
                    if player == TOP:
                        stone_count -= 1
                        new_mancalas[player] += 1
                    ind = 0

            # ran out of stones
            if stone_count == 0: 
                break

            #but if not, put a stone in a pocket and decrement stone count
            new_board[side][ind] = new_board[side][ind] + 1
            stone_count -= 1

            #do we have a capture?
            if stone_count == 0 and new_board[side][ind] == 1 and side == player: 
                captures = new_board[get_opponent(side)][ind] #if yes capture stones in the opposite pit
                new_board[get_opponent(side)][ind] = 0
                new_mancalas[player] += captures
                possible_captures += captures

            if direction: 
                ind += 1
            else: 
                ind -= 1

    if board.mancalas is None:
        total_value = 0
    if player is TOP:
        total_value = board.mancalas[TOP] - board.mancalas[BOTTOM]
    else:
        total_value = board.mancalas[BOTTOM] - board.mancalas[TOP]

    total_value = total_value + possible_captures
    return total_value