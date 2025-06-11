from enum import Enum
from piece import Piece, Piece_Type
from utils import *

class Move_Type(Enum):
    STANDARD = 1
    CASTLE_QUEENSIDE = 2
    CASTLE_KINGSIDE = 3
    EN_PASSANT = 4
    PROMOTE_PAWN = 5

class Move:
    piece: Piece = None
    dest_rank = None
    dest_file = None
    cur_rank = None
    cur_file = None
    quality = 0
    metadata = ""
    game_state = None
    promote_to: Piece_Type = None

    def __init__(self, piece, dest_rank, dest_file, move_type = Move_Type.STANDARD):
        self.piece = piece
        self.dest_rank = dest_rank
        self.dest_file = dest_file
        self.cur_rank = piece.loc_rank
        self.cur_file = piece.loc_file
        self.move_type = move_type
        self.is_white = piece.is_white
        self.quality = 0
    
    def get_notation(self):
        if self.move_type == Move_Type.CASTLE_KINGSIDE:
            return "O-O"
        elif self.move_type == Move_Type.CASTLE_QUEENSIDE:
            return "O-O-O"
        else:
            c_rank = self.dest_rank + 1
            c_file = number_to_letter(self.dest_file + 1)
            label = self.piece.get_label()
            file = number_to_letter(self.cur_file + 1)

            promotion = ""
            if self.move_type == Move_Type.PROMOTE_PAWN:
                promotion = f"={self.piece.label_map[self.promote_to]}"

            return f"{label}{file}-{c_file}{c_rank}{promotion}"

        
