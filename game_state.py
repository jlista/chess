import copy
from piece import Piece_Type
from piece import Piece
from move import Move, Move_Type
from utils import *
import time
class Game_State:
    pieces = []
    board = []
    seers_of_square = []
    seen_by_square = []
    potential_moves_to_square = []
    potential_moves_from_square = []
    white_pieces = []
    black_pieces = []
    white_king = None
    black_king = None
    white_material = 0
    black_material = 0
    white_potential_losses = 0
    black_potential_losses = 0
    is_white_in_check = False
    is_black_in_check = False

    def __init__(self):
        self.board = [[None for i in range(8)] for j in range(8)]
        self.seers_of_square = [[[] for i in range(8)] for j in range(8)]
        self.seen_by_square = [[[] for i in range(8)] for j in range(8)]
        self.potential_moves_to_square = [[[] for i in range(8)] for j in range(8)]
        self.potential_moves_from_square = [[[] for i in range(8)] for j in range(8)]
        self.pieces = []


    def make_copy(self):
        new_state = Game_State()
        for piece in self.pieces:
            new_piece = piece.copy()
            new_state.board[piece.loc_rank][piece.loc_file] = new_piece
            new_state.pieces.append(new_piece)

        new_state.past_state = self.board
        return new_state

    def setup_pieces(self):
        for i in range(8):
        
            self.pieces.append(Piece(Piece_Type.PAWN,True,1,i))
            self.pieces.append(Piece(Piece_Type.PAWN,False,6,i))

        self.pieces.append(Piece(Piece_Type.KNIGHT, True,0,1))
        self.pieces.append(Piece(Piece_Type.KNIGHT, True,0,6))

        self.pieces.append(Piece(Piece_Type.BISHOP, True,0,2))
        self.pieces.append(Piece(Piece_Type.BISHOP, True,0,5))

        self.pieces.append(Piece(Piece_Type.ROOK, True,0,0))
        self.pieces.append(Piece(Piece_Type.ROOK, True,0,7))

        self.pieces.append(Piece(Piece_Type.QUEEN, True,0,3))
        self.pieces.append(Piece(Piece_Type.KING, True,0,4))

        self.pieces.append(Piece(Piece_Type.KNIGHT, False,7,1))
        self.pieces.append(Piece(Piece_Type.KNIGHT, False,7,6))

        self.pieces.append(Piece(Piece_Type.BISHOP, False,7,2))
        self.pieces.append(Piece(Piece_Type.BISHOP, False,7,5))

        self.pieces.append(Piece(Piece_Type.ROOK, False,7,0))
        self.pieces.append(Piece(Piece_Type.ROOK, False,7,7))

        self.pieces.append(Piece(Piece_Type.QUEEN, False,7,3))
        self.pieces.append(Piece(Piece_Type.KING, False,7,4))

        for piece in self.pieces:
            self.board[piece.loc_rank][piece.loc_file] = piece

        self.calculate_seers()
        self.calculate_potential_moves()
        self.calculate_material()

    def calculate_seers(self):
        self.seers_of_square = [[[] for i in range(8)] for j in range(8)]
        for seeing_piece in self.pieces:
            seen_squares = seeing_piece.get_seen_squares(self.board)
            self.seen_by_square[seeing_piece.loc_rank][seeing_piece.loc_file] = seen_squares
            for (rank,file) in seen_squares:
                self.seers_of_square[rank][file].append(seeing_piece)

    def calculate_potential_moves(self):
        self.potential_moves_to_square = [[[] for i in range(8)] for j in range(8)]
        for seeing_piece in self.pieces:
            seen_squares = seeing_piece.get_potential_moves(self.board)
            self.potential_moves_from_square[seeing_piece.loc_rank][seeing_piece.loc_file] = seen_squares
            for (rank,file) in seen_squares:
                self.potential_moves_to_square[rank][file].append(seeing_piece)

    def get_attackers(self,rank,file,is_white):
        attackers = []
        seers = self.seers_of_square[rank][file]
        for seer in seers:
            if seer.is_white != is_white:
                attackers.append(seer)
        return attackers

    def get_defenders(self,rank,file,is_white):
        defenders = []
        seers = self.seers_of_square[rank][file]
        for seer in seers:
            if seer.is_white == is_white:
                defenders.append(seer)
        return defenders
    
    def is_in_check(self,is_white):
        in_check = False
        king = self.white_king if is_white else self.black_king
        attackers = self.get_attackers(king.loc_rank, king.loc_file, is_white)
        if len(attackers) > 0:
            in_check = True
        return in_check
    
    def is_in_dangerous_check(self,is_white):
        in_check = self.is_in_check(is_white)
        if not in_check: return False
        for piece in self.pieces:
            if piece.piece_type == Piece_Type.KING and piece.is_white == is_white:
                attackers = self.get_attackers(piece.loc_rank, piece.loc_file, is_white)

        # for now we assume there is only one checking piece - NOT a good assumption!
        checking_piece = attackers[0]

        defenders = self.get_defenders(checking_piece.loc_rank, checking_piece.loc_file, is_white)
        counterdefenders = self.get_attackers(checking_piece.loc_rank, checking_piece.loc_file, is_white)
        defenders = sorted(defenders, key = lambda x: x.value)
        if len(defenders) == 0:
            # if we can't capture the checking piece, it's dangerous
            return True
        elif len(counterdefenders) == 0:
            # if we can capture it risk-free, it's not dangerous
            return False
        else:
            # if we capture it and run into another attack, assume it's dangerous 
            # this avoids batteries, but we could use some better logic - keep this logic if the defender is the king itself
            # otherwise, calculate whether losing the defender it worth it
            return True


    def move_from_notation(self,notation, is_white):

        label_map = {
            "P": Piece_Type.PAWN,
            "N": Piece_Type.KNIGHT,
            "B": Piece_Type.BISHOP,
            "R": Piece_Type.ROOK,
            "Q": Piece_Type.QUEEN,
            "K": Piece_Type.KING
        }

        move = None
        if notation == "O-O":
            dest_rank = 5
            dest_file = 0 if is_white else 7
            mock_piece = Piece(Piece_Type.KING, is_white,None,None)
            move = Move(mock_piece,dest_rank,dest_file,Move_Type.CASTLE_KINGSIDE)

        elif notation == "O-O-O":
            dest_rank = 3
            dest_file = 0 if is_white else 7
            mock_piece = Piece(Piece_Type.KING, is_white,None,None)
            move = Move(mock_piece,dest_rank,dest_file,Move_Type.CASTLE_QUEENSIDE)

        else:
            spl = notation.split("-")
            first_part = spl[0]
            second_part = spl[1].split("=")
            promotion_type = None
            if len(second_part) == 2:
                promotion_type = second_part[1]
            dest = second_part[0]
            label = first_part[0]
            piece_type = label_map[label]
            src_file = letter_to_number(first_part[1])
            dest_file = letter_to_number(dest[0])
            dest_rank = int(dest[1]) - 1

            piece_to_move = None
            for piece in self.potential_moves_to_square[dest_rank][dest_file]:
                if piece.is_white == is_white and piece.piece_type == piece_type:
                    if piece.loc_file == src_file:
                        piece_to_move = piece

            if piece_to_move is not None:

                if promotion_type is not None:
                    move = Move(piece_to_move,dest_rank,dest_file,Move_Type.PROMOTE_PAWN)
                    move.promote_to = label_map[promotion_type]
                elif piece_to_move.piece_type == Piece_Type.PAWN and dest_file != src_file and self.board[dest_rank][dest_file] is None:
                     move = Move(piece_to_move,dest_rank,dest_file,Move_Type.EN_PASSANT)
                else:
                    move = Move(piece_to_move,dest_rank,dest_file,Move_Type.STANDARD)
        return move

    def execute(self,move: Move):
        # make sure that pawns can't be captured en passant unless they moved 2 spaces on this turn
        for piece in self.pieces:
            piece.has_just_moved_two_squares = False
        if move.piece.piece_type == Piece_Type.PAWN and abs(move.dest_rank - move.cur_rank) == 2:
            move.piece.has_just_moved_two_squares = True
        

        notation = ""
        if move.move_type == Move_Type.STANDARD:
            self.move_piece(move.piece,move.dest_rank,move.dest_file)

        if move.move_type == Move_Type.PROMOTE_PAWN:
            move.piece.piece_type = move.promote_to
            move.piece.value = move.piece.value_map[move.promote_to]
            self.move_piece(move.piece,move.dest_rank,move.dest_file)

        elif move.move_type == Move_Type.EN_PASSANT:
            self.move_piece(move.piece,move.dest_rank,move.dest_file,en_passant_capture=True)

        elif move.move_type == Move_Type.CASTLE_KINGSIDE:
            rook_start,rook_dest,king_start,king_dest,gzap = get_castling_coordinates(True,move.is_white)
            king = self.board[king_start[0]][king_start[1]]
            rook = self.board[rook_start[0]][rook_start[1]]
            self.move_piece(king,king_dest[0],king_dest[1])
            self.move_piece(rook,rook_dest[0],rook_dest[1])

        elif move.move_type == Move_Type.CASTLE_QUEENSIDE:
            rook_start,rook_dest,king_start,king_dest,gap = get_castling_coordinates(False,move.is_white)
            king = self.board[king_start[0]][king_start[1]]
            rook = self.board[rook_start[0]][rook_start[1]]
            self.move_piece(king,king_dest[0],king_dest[1])
            self.move_piece(rook,rook_dest[0],rook_dest[1])

        return notation
    def execute_hypothetical(self,move):

        hypothetical_state = self.make_copy()
        hypothetical_move = copy.deepcopy(move)
        for sp in hypothetical_state.pieces:
            if sp.loc_rank == move.piece.loc_rank and sp.loc_file == move.piece.loc_file:
                hypothetical_move.piece = sp
        start_time = time.time()
        hypothetical_state.execute(hypothetical_move)
        return hypothetical_state
    
    def move_piece(self,piece,rank,file,en_passant_capture = False):
        prev_rank = piece.loc_rank
        prev_file = piece.loc_file
        if en_passant_capture:
            occupant = self.board[prev_rank][file]
            if occupant is not None:
                self.pieces.remove(occupant)
                self.board[prev_rank][file] = None
        else:
            occupant = self.board[rank][file]
            if occupant is not None:
                self.pieces.remove(occupant)
        piece.loc_rank = rank
        piece.loc_file = file
        piece.has_moved = True
        self.board[prev_rank][prev_file] = None
        self.board[rank][file] = piece

        self.calculate_seers()
        self.calculate_potential_moves()
        self.calculate_material()
        self.is_white_in_check = self.is_in_check(True)
        self.is_black_in_check = self.is_in_check(False)

    def calculate_material(self):
        self.white_pieces = [p for p in self.pieces if p.is_white]
        self.black_pieces = [p for p in self.pieces if not p.is_white]
        self.white_king = [p for p in self.white_pieces if p.piece_type == Piece_Type.KING][0]
        self.black_king = [p for p in self.black_pieces if p.piece_type == Piece_Type.KING][0]

        # Count material
        self.white_material = sum([p.value for p in self.white_pieces if p.piece_type != Piece_Type.KING])
        self.black_material = sum([p.value for p in self.black_pieces if p.piece_type != Piece_Type.KING])