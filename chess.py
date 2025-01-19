import copy
from enum import Enum
import random
import sys
import time
from game_state import Game_State
from piece import Piece, Piece_Type
from move import Move
from evaluator import Evaluator
def print_board(board):
    for rank in range(8):
        print("---------------------------------------")
        line = ""
        for file in range(7,-1,-1):
            label = "  |"
            if board[rank][file] is not None:
                c = board[rank][file].get_label()
                if board[rank][file].is_white:
                    label = c + " |"
                else:
                    label = c + "'|"
            line += f" {label} "
        print(line)


game_state = Game_State()
game_state.setup_pieces()
is_white_move = True
eval = Evaluator()

# moves = ["Pc-c4", "Pf-f5", "Qd-c2"]

# game_state.is_white_move = True
# for m in moves:
#     game_state.execute(game_state.move_from_notation(m))
#     game_state.is_white_move = not game_state.is_white_move
#     print_board(game_state.board)

for m in range(240):

    if not is_white_move:

        start_time = time.time()
        candidates = eval.find_top_moves(game_state, is_white_move)
        end_time = time.time()
        elapsed_time = end_time - start_time



        # best_move_quality = candidates[-1].quality
        # candidate_moves = [m for m in candidates if m.quality == best_move_quality]

        # analysis_moves = candidates if len(candidates) <=5 else candidates[-5:]

        # for m in candidates: 
        #     print(f"{m.get_notation()} - {m.quality} - {m.metadata}")
        # move = random.choice(candidate_moves)
        move = candidates[0][0][0]
        print("calculated line: ")
        for m in candidates[0][0]:
            print(f"{m.get_notation()} - {m.quality}. Is white - {m.is_white}")
        game_state.execute(move)
        print(move.get_notation())
        
        print(f"Elapsed time  for all calculations: {elapsed_time} seconds")
    else:
        while True:
            move_notation = input("Please enter your move.")
            move = game_state.move_from_notation(move_notation, is_white_move)
            if move is not None and eval.is_legal_move(move,game_state):
                game_state.execute(move)
                break
            else:
                print("illegal move, please try again")



    print_board(game_state.board)
    is_white_move = not is_white_move
    #game_state.is_white_move = not game_state.is_white_move