"""
Tic Tac Toe Player
"""

import math
import numpy as np
import copy

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
    turns = []
    for i in board:
        for j in i:
            if j == None:
                turns.append(j)
    if len(turns)%2 == 1:
        return X
    else:
        return O


def actions(board):
    actions = set()
    for row in range(len(board)):
        columns = [x for x,y in enumerate(board[row]) if y == None]
        for column in columns:
            actions.add((row,column))
    return actions


def result(board, action):
    if action not in actions(board):
        raise ('Illegal Move')
    outputboard = copy.deepcopy(board)
    outputboard[action[0]][action[1]] = player(board)
    return outputboard


def winner(board):
    # diagonal win checker
    winset1 = {(0, 0), (1, 1), (2, 2)}
    winset2 = {(0, 2), (1, 1), (2, 0)}
    setX = set()
    setO = set()

    # horizontal win checker
    for row in range(len(board)):
        columnsX = [x for x, y in enumerate(board[row]) if y == X]
        for column in columnsX:
            setX.add((row, column))
        columnsO = [x for x, y in enumerate(board[row]) if y == O]
        for column in columnsO:
            setO.add((row, column))
        if winset1.issubset(setX) or winset2.issubset(setX) or all(ele == X for ele in board[row]):
            return X
        elif winset1.issubset(setO) or winset2.issubset(setO) or all(ele == O for ele in board[row]):
            return O

    # vertical win checker
    boardT = np.transpose(board)
    for row in boardT:
        if all(ele == X for ele in row):
            return X
        elif all(ele == O for ele in row):
            return O

    return None


def terminal(board):
    if winner(board) is not None:
        return True

    value = []
    for row in board:
        for col in row:
            if col is not None:
                value.append(col)

    if len(value) == 9:
        return True

    else:
        return False


def utility(board):
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


alpha_x = -math.inf
beta_x = math.inf

def minimax(board):
    global alpha_x
    global beta_x

    if player(board) == X:
        v = -math.inf
        action_X = []
        for action in actions(board):
            alpha = min_value(result(board, action))
            alpha_x = alpha
            if v < alpha:
                v = alpha
                action_X.append((action, v))
        alpha_x = -math.inf
        beta_x = math.inf
        return action_X[-1][0]

    if player(board) == O:
        v = math.inf
        action_O =  []
        for action in actions(board):
            beta = max_value(result(board,action))
            beta_x = beta
            if v > beta:
                v = beta
                action_O.append((action, v))
        alpha_x = -math.inf
        beta_x = math.inf
        return action_O[-1][0]


def max_value(board):
    global recursions
    global alpha_x
    global beta_x

    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        alpha = min_value(result(board, action))
        v = max(v, alpha)
        if alpha_x > v:
            break
    return v


def min_value(board):
    global recursions
    global alpha_x
    global beta_x

    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        beta = max_value(result(board, action))
        v = min(v, beta)
        if beta_x < v:
            break
    return v

