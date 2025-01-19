import enum 
import sys
class Piece_Type(enum.Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class Piece:
    piece_type = None
    value = sys.maxsize
    is_white = False
    loc_rank = 0
    loc_file = 0
    has_moved = False
    def __init__(self,piece_type,is_white,rank,file):
        self.piece_type = piece_type
        self.is_white = is_white
        self.loc_file = file
        self.loc_rank = rank
        if piece_type == Piece_Type.PAWN:
            self.value = 1
        if piece_type in (Piece_Type.BISHOP, Piece_Type.KNIGHT):
            self.value = 3
        if piece_type == Piece_Type.ROOK:
            self.value = 5
        if piece_type == Piece_Type.QUEEN:
            self.value = 8

    def get_label(self):
            label = "P"
            if self.piece_type == Piece_Type.KNIGHT:
                label = "N"
            if self.piece_type == Piece_Type.BISHOP:
                label = "B"
            if self.piece_type == Piece_Type.ROOK:
                label = "R"
            if self.piece_type == Piece_Type.QUEEN:
                label = "Q"
            if self.piece_type == Piece_Type.KING:
                label = "K"
            return label
    
    def get_potential_moves(self,board):
        if self.piece_type != Piece_Type.PAWN:
            return self.get_seen_squares(board)
        else:
            seen_squares = []
            if self.is_white: 
                dy = 1
            else:
                dy = -1
            if self.loc_rank + dy in range(8):
                if board[self.loc_rank+dy][self.loc_file] == None:
                    seen_squares.append((self.loc_rank+dy, self.loc_file))
                    if not self.has_moved and self.loc_rank+2*dy in range(8) and board[self.loc_rank+2*dy][self.loc_file] == None:
                        seen_squares.append((self.loc_rank+2*dy, self.loc_file))
            for diagonal in [(self.loc_rank+dy,self.loc_file-1), (self.loc_rank+dy,self.loc_file+1)]:
                if diagonal[0] in range(8) and diagonal[1] in range(8):
                    occupant = board[diagonal[0]][diagonal[1]]
                    if occupant is not None:
                        seen_squares.append(diagonal)
            return seen_squares
        
    def get_seen_squares(self,board):
        if self.piece_type == Piece_Type.PAWN:
            return self.get_seen_squares_pawn(board)
        elif self.piece_type == Piece_Type.KNIGHT:
            return self.get_seen_squares_knight(board)
        if self.piece_type == Piece_Type.BISHOP:
            return self.get_seen_squares_bishop(board)
        elif self.piece_type == Piece_Type.ROOK:
            return self.get_seen_squares_rook(board)
        elif self.piece_type == Piece_Type.QUEEN:
            return self.get_seen_squares_queen(board)
        elif self.piece_type == Piece_Type.KING:
            return self.get_seen_squares_king(board)
        else:
            return []

    def get_seen_squares_pawn(self, board):

        seen_squares = []
        if self.is_white: 
            dy = 1
        else:
            dy = -1
        for diagonal in [(self.loc_rank+dy,self.loc_file-1), (self.loc_rank+dy,self.loc_file+1)]:
            if diagonal[0] in range(8) and diagonal[1] in range(8):
                seen_squares.append(diagonal)
        #print(seen_squares)
        return seen_squares

    def get_seen_squares_knight(self, board):
        seen_squares = []
        displacements = [(1,2),(2,1),(-1,2),(2,-1),(1,-2),(-2,1),(-1,-2),(-2,-1)]
        for displacement in displacements:
            rank = self.loc_rank + displacement[0]
            file = self.loc_file + displacement[1]
            if rank in range(8) and file in range(8):
                seen_squares.append((rank,file))
        return seen_squares
    
    def get_seen_squares_bishop(self, board):
        seen_squares = []

        diag_dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]

        for dirs in diag_dirs:
            rank = self.loc_rank + dirs[0]
            file = self.loc_file + dirs[1]
            while rank in range(8) and file in range(8):
                occupant = board[rank][file]
                seen_squares.append((rank,file))
                if occupant is not None:
                    break
                rank += dirs[0]
                file += dirs[1]
        return seen_squares
    
    def get_seen_squares_rook(self, board):
        seen_squares = []

        diag_dirs = [(1,0),(-1,0),(0,1),(0,-1)]

        for dirs in diag_dirs:
            rank = self.loc_rank + dirs[0]
            file = self.loc_file + dirs[1]
            while rank in range(8) and file in range(8):
                occupant = board[rank][file]
                seen_squares.append((rank,file))
                if occupant is not None:
                    break
                rank += dirs[0]
                file += dirs[1]
        return seen_squares
    
    def get_seen_squares_queen(self, board):
        seen_squares = []

        diag_dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(-1,1),(1,-1)]

        for dirs in diag_dirs:
            rank = self.loc_rank + dirs[0]
            file = self.loc_file + dirs[1]
            while rank in range(8) and file in range(8):
                occupant = board[rank][file]
                seen_squares.append((rank,file))
                if occupant is not None:
                    break
                rank += dirs[0]
                file += dirs[1]
        return seen_squares
    
    
    def get_seen_squares_king(self, board):
        seen_squares = []

        diag_dirs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]

        for dirs in diag_dirs:
            rank = self.loc_rank + dirs[0]
            file = self.loc_file + dirs[1]
            if rank in range(8) and file in range(8):
                seen_squares.append((rank,file))

        return seen_squares