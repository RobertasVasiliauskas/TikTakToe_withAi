import math
import PySimpleGUI as sg
import numpy as np
from copy import deepcopy as deep_copy
import random

WIDTH, HEIGHT = 600, 600
CELL_SIZE = WIDTH // 3

def calculate_cell(x, y):
    row = 2 - (y // CELL_SIZE)
    col = x // CELL_SIZE
    return int(row), int(col)

def get_cell_center(x, y):
    center_x = (y + 0.5) * CELL_SIZE
    center_y = (2 - x + 0.5) * CELL_SIZE
    return center_x, center_y

def check_rows(board):
    for row in board:
        if -1 not in row:
            without_negatives = set(row)
            if len(without_negatives) == 1:
                return row[0]
    return -1

def check_diagonals(board):
    if board[0][0] == board[1][1] == board[2][2] != -1:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != -1:
        return board[0][2]
    return -1

def check_for_draw(board):
    for row in board:
        if -1 in row:
            return 0
    return -2

def check_for_win(board):
    for new_board in [board, np.transpose(board)]:
        result = check_rows(new_board)
        if result != -1:
            return result
        result = check_diagonals(new_board)
        if result != -1:
            return result

    if check_for_draw(board) == -2:
        return -2

    return -1

def minimax(isMaxTurn, maximizerMark, board):
    winner = check_for_win(board)
    if winner != -1:
        if winner == -2:
            return 0
        return 1 if winner == maximizerMark else -1

    scores = []
    for move in get_possible_moves(board):
        board[move[0]][move[1]] = maximizerMark if isMaxTurn else 1 - maximizerMark
        score = minimax(not isMaxTurn, maximizerMark, board)
        scores.append(score)
        board[move[0]][move[1]] = -1

    return max(scores) if isMaxTurn else min(scores)

def get_possible_moves(board):
    moves = []
    for row in range(3):
        for col in range(3):
            if board[row][col] == -1:
                moves.append((row, col))
    return moves

def ai_move(board):
    best_score = -math.inf
    best_move = None
    for move in get_possible_moves(board):
        board[move[0]][move[1]] = 0  # AI is always player '0'
        score = minimax(False, 0, board)
        board[move[0]][move[1]] = -1
        if score > best_score:
            best_score = score
            best_move = move

    board[best_move[0]][best_move[1]] = 0

def render_move(graph, board):
    for row in range(3):
        for col in range(3):
            center_x, center_y = get_cell_center(row, col)
            if board[row][col] == 0:
                graph.draw_circle(
                    (center_x, center_y),
                    CELL_SIZE // 2 - 10,
                    line_color='black',
                    line_width=5
                )
            elif board[row][col] == 1:
                offset = CELL_SIZE // 3
                graph.draw_line(
                    (center_x - offset, center_y - offset),
                    (center_x + offset, center_y + offset),
                    color='blue',
                    width=5
                )
                graph.draw_line(
                    (center_x - offset, center_y + offset),
                    (center_x + offset, center_y - offset),
                    color='blue',
                    width=5
                )

if __name__ == '__main__':
    turn = random.choice([True, False])

    board = [[-1 for _ in range(3)] for _ in range(3)]

    graph = sg.Graph(
        canvas_size=(600, 600),
        graph_bottom_left=(0, 0),
        graph_top_right=(600, 600),
        enable_events=True,
        key='graph',
        background_color='white'
    )

    layout = [[sg.Checkbox('Player', default=True, enable_events=True, key='checkbox'), graph]]
    window = sg.Window('TikTakToe', layout, resizable=False, finalize=True)

    # Draw grid lines
    graph.draw_line((0.33 * WIDTH, 0), (0.33 * WIDTH, HEIGHT))
    graph.draw_line((0.66 * WIDTH, 0), (0.66 * WIDTH, HEIGHT))
    graph.draw_line((0, 0.33 * HEIGHT), (WIDTH, 0.33 * HEIGHT))
    graph.draw_line((0, 0.66 * HEIGHT), (WIDTH, 0.66 * HEIGHT))

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        if event == 'checkbox' and not values['checkbox']:
            if not turn:
                if check_for_win(board) == -1:  # Only make AI move if the game is not won
                    ai_move(board)
                    render_move(graph, board)
                    turn = not turn

        if event == 'graph':
            cell = calculate_cell(values['graph'][0], values['graph'][1])
            if values['checkbox']:
                if board[cell[0]][cell[1]] == -1:
                    board[cell[0]][cell[1]] = 1 if turn else 0
                    render_move(graph, board)
                    turn = not turn
            else:
                if turn and board[cell[0]][cell[1]] == -1:
                    board[cell[0]][cell[1]] = 1
                    render_move(graph, board)
                    turn = not turn

                    if not turn and check_for_win(board) == -1:  # Only make AI move if the game is not won
                        ai_move(board)
                        render_move(graph, board)
                        turn = not turn

        game_status = check_for_win(board)
        if game_status != -1:
            if game_status == -2:
                print("Draw")
            else:
                print(f"Player {game_status} wins!")
            break

    window.close()
