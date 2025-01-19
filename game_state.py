import copy
from piece import Piece_Type
from piece import Piece
from move import Move, Move_Type
from utils import *
import time
class Game_State:
    pieces = []
    board = []
    seers = []
    potential_moves = []
    past_states = []
    #is_white_move = True

    has_white_castled = False
    has_black_castled = False

    def __init__(self):
        self.board = [[None for i in range(8)] for j in range(8)]
        self.seers = [[[] for i in range(8)] for j in range(8)]
        self.potential_moves = [[[] for i in range(8)] for j in range(8)]
        self.pieces = []

    def make_copy(self):
        new_state = Game_State()
        new_state.pieces = copy.deepcopy(self.pieces)
        for piece in new_state.pieces:
            new_state.board[piece.loc_rank][piece.loc_file] = piece
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

    def calculate_seers(self):
        start_time=time.time()  
      
        for seeing_piece in self.pieces:
            seen_squares = seeing_piece.get_seen_squares(self.board)
            for (rank,file) in seen_squares:
                self.seers[rank][file].append(seeing_piece)
                
        end_time = time.time()
        elapsed_time = end_time - start_time

        #print(f"Elapsed time for find_seers: {elapsed_time} seconds")


    def find_seers(self,rank,file):
        start_time=time.time()
        seers = []
        for seeing_piece in self.pieces:
            seen_squares = seeing_piece.get_seen_squares(self.board)
            if (rank,file) in seen_squares:
                seers.append(seeing_piece)
        end_time = time.time()
        elapsed_time = end_time - start_time

        #print(f"Elapsed time for find_seers: {elapsed_time} seconds")
        return seers
    
    def calculate_potential_moves(self):
        start_time=time.time()  
      
        for seeing_piece in self.pieces:
            seen_squares = seeing_piece.get_potential_moves(self.board)
            for (rank,file) in seen_squares:
                self.potential_moves[rank][file].append(seeing_piece)
                
        end_time = time.time()
        elapsed_time = end_time - start_time

        #print(f"Elapsed time for  find_pm: {elapsed_time} seconds")
    
    def find_potential_moves(self,rank,file):
        start_time = time.time()
        seers = []
        for seeing_piece in self.pieces:
            seen_squares = seeing_piece.get_potential_moves(self.board)
            if (rank,file) in seen_squares:
                seers.append(seeing_piece)
        end_time = time.time()
        elapsed_time = end_time - start_time

        #print(f"Elapsed time for find_potential_moves: {elapsed_time} seconds")
        return seers

    def get_attackers(self,rank,file,is_white):
        attackers = []
        seers = self.seers[rank][file]
        for seer in seers:
            if seer.is_white != is_white:
                attackers.append(seer)
        return attackers

    def get_defenders(self,rank,file,is_white):
        defenders = []
        seers = self.seers[rank][file]
        for seer in seers:
            if seer.is_white == is_white:
                defenders.append(seer)
        return defenders
    
    def is_in_check(self,is_white):
        in_check = False
        for piece in self.pieces:
            if piece.piece_type == Piece_Type.KING and piece.is_white == is_white:
                attackers = self.get_attackers(piece.loc_rank, piece.loc_file, is_white)
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
            source = spl[0]
            dest = spl[1]
            label = source[0]
            piece_type = label_map[label]
            src_file = letter_to_number(source[1])
            dest_file = letter_to_number(dest[0])
            dest_rank = int(dest[1]) - 1

            piece_to_move = None
            for piece in self.find_potential_moves(dest_rank,dest_file):
                if piece.is_white == is_white and piece.piece_type == piece_type:
                    if piece.loc_file == src_file:
                        piece_to_move = piece
            if piece_to_move is not None:
     
                move = Move(piece_to_move,dest_rank,dest_file,Move_Type.STANDARD)

        return move




    def execute(self,move: Move):
        notation = ""
        if move.move_type == Move_Type.STANDARD:

            self.move_piece(move.piece,move.dest_rank,move.dest_file)

        elif move.move_type == Move_Type.CASTLE_KINGSIDE:
            rook_start,rook_dest,king_start,king_dest,gap = get_castling_coordinates(True,move.is_white)
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

        start_time = time.time()
        hypothetical_state = self.make_copy()
        hypothetical_move = copy.deepcopy(move)
        end_time = time.time()
        elapsed_time = end_time - start_time

        #print(f"Elapsed time copying spoof state: {elapsed_time} seconds")
        for sp in hypothetical_state.pieces:
            if sp.loc_rank == move.piece.loc_rank and sp.loc_file == move.piece.loc_file:
                hypothetical_move.piece = sp
        start_time = time.time()
        hypothetical_state.execute(hypothetical_move)

        end_time = time.time()
        elapsed_time = end_time - start_time

        #print(f"Elapsed time executing hypothetical move: {elapsed_time} seconds")
        return hypothetical_state
    
    def move_piece(self,piece,rank,file):
        prev_rank = piece.loc_rank
        prev_file = piece.loc_file
        occupant = self.board[rank][file]
        if occupant is not None:
            self.pieces.remove(occupant)
        piece.loc_rank = rank
        piece.loc_file = file
        piece.has_moved = True
        self.board[prev_rank][prev_file] = None
        self.board[rank][file] = piece

        ## todo come up with a real way of  handling pawn promotion
        if piece.piece_type == Piece_Type.PAWN and rank in (0,7):
            piece.piece_type = Piece_Type.QUEEN

        start_time = time.time()
        self.calculate_seers()
        self.calculate_potential_moves()
        #self.is_white_move = not self.is_white_move
        # for r in range(8):
        #     for f in range(8):
        #         self.seers[r][f] = self.find_seers(r,f)

        #         self.potential_moves[r][f] = self.find_potential_moves(r,f)
        end_time = time.time()
        elapsed_time = end_time - start_time

        #print(f"Elapsed time finding seers: {elapsed_time} seconds")
