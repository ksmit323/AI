"""
Tic Tac Toe Player
"""

import math
import copy
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # If at initial state, X moves first
    if board == initial_state():
        return X

    # Initialize variables
    x = 0
    o = 0

    # Loop through board to track who goes next
    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                x += 1
            elif board[i][j] == O:
                o += 1
    if x > o:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Check that game is not over.  If it is, return any value
    if terminal(board):
        return 0

    # Initialize list for all possible moves
    moves = set()

    # Loop thru board to find all empty cells
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                moves.add((i,j))

    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Check if action is valid
    if action not in actions(board):
        raise ValueError("Not a valid move")

    # Make a deep copy so original board remains unchanged
    board_copy = copy.deepcopy(board)

    # Update board with player's action
    i, j = action
    board_copy[i][j] = player(board)

    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check for horizontal winner
    for i in range(3):
        if board[i] == [X, X, X]:
            return X
        elif board[i] == [O, O, O]:
            return O

    # Check for vertical winner
    for i in range(3):
        x_v = 0
        o_v = 0
        for j in range(3):
            if board[j][i] == X:
                x_v += 1
            elif board[j][i] == O:
                o_v += 1
        if x_v == 3:
            return X
        elif o_v == 3:
            return O

    # Check for top-bottom diagonal winner
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]

    # Check for bottom-top diagonal winner
    if board[2][0] == board[1][1] == board[0][2] and board[2][0] != EMPTY:
        return board[2][0]
    
    return None
        

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if there is a winner
    win = winner(board)
    if win == X or win == O:
        return True

    # Check if all cells have been filled
    empty = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                empty += 1
    if empty > 0:
        return False

    # Check for a tie
    elif empty == 0 and win == None:
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Check if game is over
    if terminal(board):
        return None

    # Define optimal move for X player
    def max_value(board):
        if terminal(board):
            return utility(board)
        v = -math.inf
        for action in actions(board):
            v = max(v, min_value(result(board, action)))
        return v

    # Define optimal move for O player
    def min_value(board):
        if terminal(board):
            return utility(board)
        v = math.inf
        for action in actions(board):
            v = min(v, max_value(result(board, action)))
        return v

    # Choose optimal move for O
    if player(board) == O:
        v = math.inf
        move = ()
        for action in actions(board):
            if len(move) == 0:
                move = action
            max_v = max_value(result(board, action))
            if max_v < v:
                move = action
            v = min(v, max_v)
            if v == -1:
                return action
        return move

        # Choose optimal move for X
    else:
        v = -math.inf
        moves = []
        for action in actions(board):
            min_v = min_value(result(board, action))
            if min_v > v:
                moves.clear()
                moves.append(action)
            elif min_v == v:
                moves.append(action)
            v = max(v, min_v)
            if v == 1:
                return action
        return random.choice(moves)
