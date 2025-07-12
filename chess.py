import json
import re
import sys
from game_state import Game_State
from evaluator import Evaluator

MOVE_REGEX = r'[PNBRQK][a-h]-[a-h][1-8]$|O-O$|O-O-O$|[PNBRQK][a-h]-[a-h][1-8]=[NBRQ]$'

eval = Evaluator()

def make_computer_move(game_state):
    # use the engine to make a move
    global Evaluator

    move = eval.find_next_move(game_state,False)
    game_state.execute(move)
    return move.get_notation()
    
def make_human_move(game_state, is_white_move):
    # execute a move that was entered by the human player
    while True:
        move_notation = input("Please enter your move: ")
        if re.match(MOVE_REGEX,move_notation):
            move = game_state.move_from_notation(move_notation, is_white_move)
            if move is not None and eval.is_legal_move(move,game_state):
                game_state.execute(move)
                return(move_notation)
            else:
                print("Illegal move, please try again.")
        else:
            print("Could not parse move notation, please try again.")

def make_setup_move(m,game_state,is_white_move):
    # execute a move that was provided as part of the game's starting state
    if re.match(MOVE_REGEX,m):
        move = game_state.move_from_notation(m, is_white_move)
        if move is not None and eval.is_legal_move(move,game_state):
            game_state.execute(move)
        else:
            print(f"Move {m} is illegal, exiting game.")
            sys.exit(1)
    else:
        print(f"Move {m} is not recognized, exiting game.")
        sys.exit(1)    

def print_board(board, forward):
    if forward: 
        rank_range = (7,-1,-1)
        file_range = (0,8,1)
    else: 
        rank_range = (0,8,1)
        file_range = (7,-1,-1)

    for rank in range(*rank_range):
        print("---------------------------------------")
        line = ""
        for file in range(*file_range):
            label = "  |"
            if board[rank][file] is not None:
                c = board[rank][file].get_label()
                if board[rank][file].is_white:
                    label = c + " |"
                else:
                    label = c + "'|"
            line += f" {label} "
        print(line)

def main():

    game_state = Game_State()
    game_state.setup_pieces()

    is_white_move = True
    game_sequence = []

    starting_state = input("Enter game starting state: ")
    if starting_state:
        try:
            sequence = json.loads(starting_state)
        except Exception as e:
            print("Could not parse starting move sequence, exiting game.")
            sys.exit(1)
        for m in sequence:
            make_setup_move(m,game_state,is_white_move)
            game_sequence.append(m)
            is_white_move = not is_white_move
    else:
        print("Starting with default configuration.")
    print_board(game_state.board, True)

    while True:
        if not is_white_move:
            m = make_computer_move(game_state)
            print(f"Chosen move: {m}")
        else:
            m = make_human_move(game_state,is_white_move)
        game_sequence.append(m)
        print_board(game_state.board, True)
        print(game_sequence)
        is_white_move = not is_white_move

if __name__=="__main__":
    main()