from enum import Enum
from piece import Piece

class Move_Type(Enum):
    STANDARD = 1
    CASTLE_QUEENSIDE = 2
    CASTLE_KINGSIDE = 3
    EN_PASSANT = 4
    PROMOTE_QUEEN = 5
    PROMOTE_ROOK = 6
    PROMOTE_BISHOP = 7
    PROMOTE_KNIGHT = 8

class Move:
    piece: Piece = None
    dest_rank = None
    dest_file = None
    cur_rank = None
    cur_file = None
    quality = 0
    metadata = ""
    game_state = None
    def __init__(self, piece, dest_rank, dest_file, move_type = Move_Type.STANDARD):
        self.piece = piece
        self.dest_rank = dest_rank
        self.dest_file = dest_file
        self.cur_rank = piece.loc_rank
        self.cur_file = piece.loc_file
        self.move_type = move_type
        self.is_white = piece.is_white
        self.quality = 0

        
    def number_to_letter(self, n):
        """
        takes in a number and returns a lowercase letter where a=1, b=2, etc.
        """
        return chr(n+96)
    
    


    def get_notation(self):
        if self.move_type == Move_Type.STANDARD:
            c_rank = self.dest_rank + 1
            c_file = self.number_to_letter(self.dest_file + 1)
            label = self.piece.get_label()
            file = self.number_to_letter(self.cur_file + 1)
            return f"{label}{file}-{c_file}{c_rank}"
        elif self.move_type == Move_Type.CASTLE_KINGSIDE:
            return "O-O"
        elif self.move_type == Move_Type.CASTLE_QUEENSIDE:
            return "O-O-O"
