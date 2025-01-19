import sys
import time
from move import Move, Move_Type
from game_state import Game_State
from piece import Piece, Piece_Type
from typing import List
from utils import *
class Evaluator:

    def find_legal_moves(self, game_state, is_white):
        legal_moves = []
        for piece in game_state.pieces:
            if piece.is_white == is_white:
                candidates = piece.get_potential_moves(game_state.board)
                for candidate in candidates:
                    move = Move(piece,candidate[0],candidate[1])
                    if self.is_legal_move(move,game_state):
                        legal_moves.append(move)

        if self.can_castle(game_state,is_white, True):
            dest_file = 6
            dest_rank = 0 if is_white else 7
            mock_piece = Piece(Piece_Type.KING, is_white,dest_rank,4)
            move = Move(mock_piece,dest_rank,dest_file,Move_Type.CASTLE_KINGSIDE)
            if not self.does_move_put_player_in_check(move, game_state):
                legal_moves.append(move)

        if self.can_castle(game_state,is_white, False):
            dest_file = 2
            dest_rank = 0 if is_white else 7
            mock_piece = Piece(Piece_Type.KING, is_white,dest_rank,4)
            move = Move(mock_piece,dest_rank,dest_file,Move_Type.CASTLE_QUEENSIDE)
            if not self.does_move_put_player_in_check(move,game_state):
                legal_moves.append(move)

        return legal_moves
    
    def is_legal_move(self, move: Move, game_state: Game_State):
        if move.dest_file == 5 and move.dest_rank == 6 and move.piece.piece_type == Piece_Type.KING:
            print("fffff")
        if move.move_type == Move_Type.CASTLE_KINGSIDE:
            return self.can_castle(game_state,move.is_white,True)
        if move.move_type == Move_Type.CASTLE_QUEENSIDE:
            return self.can_castle(game_state,move.is_white,False)
        move_blocked = self.is_move_blocked(move,game_state)
        in_check = self.does_move_put_player_in_check(move,game_state)
        return not (move_blocked or in_check)

    def is_move_blocked(self,move: Move,game_state: Game_State):
        
        occupant = game_state.board[move.dest_rank][move.dest_file]
        if occupant is None or occupant.is_white != move.is_white:
            # c_rank = candidate[0] + 1
            # c_file = number_to_letter(candidate[1] + 1)
            # label = piece.get_label()
            #print(f"{label}{file} -> {c_file}{c_rank}")
            return False
        
        return True

    def does_move_put_player_in_check(self,move: Move,game_state: Game_State):
        # if  move.piece.piece_type == Piece_Type.KING and move.cur_rank == 7:
        #     print("gotcha!")
        spoof_state = game_state.execute_hypothetical(move)
        move.game_state = spoof_state
        if spoof_state.is_in_check(move.is_white):
            return True
        return False
    


    def can_castle(self, game_state, is_white, is_kingside):
        rook_start,rook_dest,king_start,king_dest,gap = get_castling_coordinates(is_kingside, is_white)
        
        rook_start_occupant = game_state.board[rook_start[0]][rook_start[1]]
        king_start_occupant = game_state.board[king_start[0]][king_start[1]]
        rook_dest_occupant = game_state.board[rook_dest[0]][rook_dest[1]]
        king_dest_occupant = game_state.board[king_dest[0]][king_dest[1]] 
        gap_occupant = None
        if not is_kingside:
            gap_occupant = game_state.board[gap[0]][gap[1]] 

        rook_can_castle = False
        king_can_castle = False
        coast_is_clear = False

        if rook_start_occupant is not None and \
        rook_start_occupant.piece_type == Piece_Type.ROOK and \
        not rook_start_occupant.has_moved:
            rook_can_castle = True

        if king_start_occupant is not None and \
        king_start_occupant.piece_type == Piece_Type.KING and \
        not king_start_occupant.has_moved:
            king_can_castle = True

        if rook_dest_occupant is None and king_dest_occupant is None:
            attackers1 = game_state.get_attackers(king_start[0],king_start[1],is_white)
            attackers2 = game_state.get_attackers(king_dest[0],king_dest[1],is_white)
            attackers3 = game_state.get_attackers(rook_dest[0],rook_dest[1],is_white)

            if len(attackers1 + attackers2 + attackers3) == 0 and gap_occupant == None:
                coast_is_clear = True
        
        return rook_can_castle and king_can_castle and coast_is_clear


        """
        How to calculate a move:

        Find_lines (line, state, depth):

        possible_moves = get possible moves (state)
        for move in possible moves:
        responses = get_possible_responses
        for response in responses:
            evaluate position and assume opponent will play the best move for them.
            lines.append(line, possible_move, strongest_opponent_response)

        of the lines found, pick the few that are best for us and recurse.

        

        """

    lines = [[],[]]
    def find_lines(self,line,game_state,depth,is_white):
        # This is assuming we are calculating for black. Can be made dynamic
        #game_state.is_white_move = False
        legal_moves = self.find_legal_moves(game_state,is_white)
        for move in legal_moves:
            if move.get_notation() == "Ng-f6":
                print("fff")
            spoof_state: Game_State = move.game_state
            #spoof_state.is_white_move = not game_state.is_white_move
            move.quality = self.rate_move_quality_heuristic(move,spoof_state)
            newline = [move]
            responses = self.find_legal_moves(spoof_state, not is_white)
            best_response_q = -999999999999
            best_response = None
            for response in responses:
                spoof_state2: Game_State = response.game_state
                #spoof_state.is_white_move = game_state.is_white_move

                response.quality = self.rate_move_quality_heuristic(response,spoof_state2)
                newline2 = newline + [response]
                #print(newline2)
                if response.quality > best_response_q:
                    best_response_q = response.quality
                    best_response = response
            self.lines[depth].append(line + newline + [best_response])
            print(f"the best response to {move.get_notation()} - {move.quality} is {best_response.get_notation()} - {best_response_q}")
        
        self.lines[depth] = sorted(self.lines[depth], key = lambda x: x[-1].quality)
        if depth == 0:
            return

        candidates = self.lines[depth][0:5]
        for candidate in candidates:
            return self.find_lines(candidate,candidate[-1].game_state,depth-1,is_white)
        print("fff")

    def find_top_moves(self, game_state, is_white):
        self.lines = [[],[]]
        self.find_lines([],game_state,1,is_white)
        return self.lines

    def get_top_moves(self,game_state):

        candidates = []
        print("FINDING LEGAL MOVES")
        start_time = time.time()
        legal_moves = self.find_legal_moves(game_state)
        end_time = time.time()
        elapsed_time = end_time - start_time

        #print(f"Elapsed time legal moves: {elapsed_time} seconds")
        for move in legal_moves:
            start_time = time.time()
            spoof_state: Game_State = game_state.execute_hypothetical(move)
            #spoof_state.is_white_move = not game_state.is_white_move

            end_time = time.time()
            elapsed_time = end_time - start_time

            #print(f"Elapsed time for spoof state: {elapsed_time} seconds")
            move.quality = self.rate_move_quality_heuristic(move,spoof_state)
            candidates.append((move,spoof_state))

        best_candidates = sorted(candidates,key=lambda x: x[0].quality)
        worst_outcome_for_opponent = 99999999
        move_choice = None
        for candidate in best_candidates:
            opponent_moves = self.find_legal_moves(candidate[1])
            for opponent_move in opponent_moves:
                spoof_state: Game_State = game_state.execute_hypothetical(opponent_move)
                #spoof_state.is_white_move = game_state.is_white_move
                opponent_move.quality = self.rate_move_quality_heuristic(opponent_move,spoof_state)
            opponent_moves = sorted(opponent_moves, key = lambda x: x.quality)
            best_opponent_move = opponent_moves[-1]
            if best_opponent_move.quality < worst_outcome_for_opponent:
                worst_outcome_for_opponent = best_opponent_move.quality
                move_choice = candidate


        # passes_round_2 = False
        # candidate_index = -1
        # while not passes_round_2 and candidate_index >= -1*len(legal_moves):
        #     candidate = legal_moves[candidate_index]
        #     spoof_state = game_state.execute_hypothetical(candidate)
        #     spoof_state.is_white_move = not game_state.is_white_move
        #     can_opponent_check = False
        #     opponent_moves = self.find_legal_moves(spoof_state)
        #     for opponent_move in opponent_moves:
        #         metaspoof = spoof_state.execute_hypothetical(opponent_move)
        #         if metaspoof.is_in_dangerous_check(game_state.is_white_move):
        #             can_opponent_check = True
        #             break
        #     if not can_opponent_check:
        #         passes_round_2 = True      
        #     else: 
        #         candidate.quality -= 50000
        #         candidate_index -= 1


        return [move_choice[0]]
    
    def rate_move_quality_heuristic(self,move,spoof_state: Game_State):
        
        start_time = time.time()
        quality = 0

        white_pieces = [p for p in spoof_state.pieces if p.is_white]
        black_pieces = [p for p in spoof_state.pieces if not p.is_white]
        white_king = [p for p in white_pieces if p.piece_type == Piece_Type.KING][0]
        black_king = [p for p in black_pieces if p.piece_type == Piece_Type.KING][0]

        # Count material
        white_material = sum([p.value for p in white_pieces if p.piece_type != Piece_Type.KING])
        black_material = sum([p.value for p in black_pieces if p.piece_type != Piece_Type.KING])

        # Count seen squares
        white_squares_seen = []
        for sqset in [p.get_seen_squares(spoof_state.board) for p in white_pieces]:
            white_squares_seen += sqset
        black_squares_seen = []
        for sqset in [p.get_seen_squares(spoof_state.board) for p in black_pieces]:
            black_squares_seen += sqset

        # Count seen critical squares
        central_squares = [(3,3),(3,4),(4,3),(4,4)]
        white_king_adjacent_squares = white_king.get_seen_squares(spoof_state.board)
        black_king_adjacent_squares = black_king.get_seen_squares(spoof_state.board)
        white_critical_squares = central_squares + black_king_adjacent_squares
        black_critical_squares = central_squares + white_king_adjacent_squares

        white_seen_critical_squares = len([s for s in white_squares_seen if s in white_critical_squares])
        black_seen_critical_squares = len([s for s in black_squares_seen if s in black_critical_squares])
        white_squares_seen = len(white_squares_seen)
        black_squares_seen = len(black_squares_seen)

        # # Count developed pieces
        # current_developed_pieces = sum([1 for p in current_pieces if p.has_moved])
        # opponent_developed_pieces = sum([1 for p in opponent_pieces if p.has_moved])

        # Count defenders
        white_defenders = sum([len(spoof_state.get_defenders(p.loc_rank,p.loc_file,True)) for p in white_pieces])
        black_defenders = sum([len(spoof_state.get_defenders(p.loc_rank,p.loc_file,False)) for p in black_pieces])

        # Count attackers
        white_attackers = sum([len(spoof_state.get_attackers(p.loc_rank,p.loc_file,False)) for p in black_pieces])
        black_attackers = sum([len(spoof_state.get_attackers(p.loc_rank,p.loc_file,True)) for p in white_pieces])

        material_score = 20 * (white_material - black_material)
        move.metadata += f"Material: {material_score} "
        seen_score = white_squares_seen - black_squares_seen
        move.metadata += f"Seen: {seen_score} "
        critical_seen_score = 4 * (white_seen_critical_squares - black_seen_critical_squares)
        move.metadata += f"Critical: {critical_seen_score} "
        defender_score = 3 * (white_defenders - black_defenders)
        move.metadata += f"Defenders: {defender_score} "
        attacker_score = 3 * (white_attackers - black_attackers)
        move.metadata += f"Attackers: {attacker_score} "

        quality = material_score + seen_score + critical_seen_score + defender_score + attacker_score
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        #print(f"Elapsed time: {elapsed_time} seconds")

        return quality

        #print(f"Move: {candidate.get_notation()}, q = {candidate.quality}")
    def rate_move_quality_backup(self,move, game_state):
        capturing = False
        likely_to_be_captured = False
        spoof_state = game_state.execute_hypothetical(move)
        quality = 0
        # heuristic 1: does the move put the opponent in checkmate?
        # simulate possible moves for opponent
        spoof_state.is_white_move = not game_state.is_white_move

    
        # heuristic 4: if I capture here, how many material do i win?
        # 4.1 if I move here, what is the worst capture the opponent can do on any square?


        material_gain = 0
        occupant = game_state.board[move.dest_rank][move.dest_file]

        if occupant is not None:
            material_gain = occupant.value
            capturing = True

        largest_hypothetical_loss = 0
        largest_piece_to_lose = None
        for piece in spoof_state.pieces:
            if piece.is_white == move.is_white:
                hypothetical_loss = 0
                enemy_attackers = sorted(spoof_state.get_attackers(piece.loc_rank,piece.loc_file,move.is_white), key = lambda x: x.value)
                defenders = sorted(spoof_state.get_defenders(piece.loc_rank,piece.loc_file,move.is_white), key = lambda x: x.value)
                if len(enemy_attackers) > 0:
                    weakest_attacker = enemy_attackers[0]
                    if len(defenders) == 0 or weakest_attacker.value <= piece.value:
                        hypothetical_loss = piece.value
                        largest_piece_to_lose = piece
                if hypothetical_loss > largest_hypothetical_loss:
                    largest_hypothetical_loss = hypothetical_loss
        material_gain -= largest_hypothetical_loss

        if largest_hypothetical_loss > 0 and largest_piece_to_lose.piece_type == move.piece.piece_type:
            likely_to_be_captured = True
           

        quality += 10000*material_gain
        move.metadata += f"Material: {material_gain} "

        if spoof_state.is_in_dangerous_check(not move.is_white):
            quality += 10000 
            move.metadata += f"Dangerous check detected. "
            if len(self.find_legal_moves(spoof_state)) == 0:
                move.metadata += f"Checkmate detected. "
                quality = sys.maxsize

        # how much material am I attacking?

        attacked_material_before = 0
        for piece in game_state.pieces:
            if piece.is_white != move.is_white and piece.piece_type != Piece_Type.KING:
                attackers = game_state.get_attackers(piece.loc_rank,piece.loc_file,not move.is_white)
                if len(attackers) > 0:
                    attacked_material_before += piece.value

        attacked_material = 0
        for piece in spoof_state.pieces:
            if piece.is_white != move.is_white and piece.piece_type != Piece_Type.KING:
                attackers = spoof_state.get_attackers(piece.loc_rank,piece.loc_file,not move.is_white)
                if len(attackers) > 0:
                    attacked_material += piece.value

        attacked_material_delta = attacked_material - attacked_material_before
        if not likely_to_be_captured:
            quality += 150 * attacked_material_delta
            move.metadata += f"Attacking material: {attacked_material_delta} "

        # prefer to capture with pieces rather than pawns
        if capturing:
            if move.piece.piece_type == Piece_Type.PAWN:
                quality -= 200
                move.metadata += f"Capturing w/pawn discouraged. "


        # is there an improvement in how many squares the piece will see?
        # this mainly matters in the endgame - use number of pieces on the board as a proxy
        CUTOFF = 17
        if len([p for p in spoof_state.pieces if p.is_white != move.is_white]) < CUTOFF:

            total_squares_seen_before = 0
            for piece in game_state.pieces:
                if piece.is_white == move.is_white:
                    total_squares_seen_before += len(piece.get_seen_squares(game_state.board))
        

            total_squares_seen_after = 0
            for piece in spoof_state.pieces:
                if piece.is_white == move.is_white:
                    total_squares_seen_after += len(piece.get_seen_squares(spoof_state.board))
                 
            improvement = total_squares_seen_after - total_squares_seen_before
            if not likely_to_be_captured:
                quality += 50 * improvement
                move.metadata += f"Improvement in seen squares: {improvement} "

        if not move.piece.has_moved: 
            quality += 150
            move.metadata += "Moving new piece. "
        if move.move_type == Move_Type.CASTLE_KINGSIDE or move.move_type == Move_Type.CASTLE_QUEENSIDE:
            move.metadata += "Castling is good. "
            quality += 500

        # try to attack squares that the enemy king sees
        king_confiners_before = 0
        king_confiners_after = 0
        for piece in spoof_state.pieces:
            if piece.piece_type == Piece_Type.KING and piece.is_white != move.is_white:
                for s in piece.get_seen_squares(spoof_state.board):
                    if spoof_state.get_attackers(s[0],s[1],not move.is_white):
                        king_confiners_after += 1

        for piece in game_state.pieces:
            if piece.piece_type == Piece_Type.KING and piece.is_white != move.is_white:
             for s in piece.get_seen_squares(game_state.board):
                    if game_state.get_attackers(s[0],s[1],not move.is_white):
                        king_confiners_before += 1

        if (king_confiners_after - king_confiners_before) != 0 and not likely_to_be_captured:
            quality += 500 * (king_confiners_after - king_confiners_before)
            move.metadata += f"{(king_confiners_after - king_confiners_before)} more squares attacked around king. "        



        rank_ctr_dist = abs(move.dest_rank - 3.5)
        file_ctr_dist = abs(move.dest_file - 3.5)
        if move.piece.piece_type != Piece_Type.KING:
            quality += (35 - rank_ctr_dist - file_ctr_dist)

        return quality
    
        # problem - doesn't seem to recognize you can protect a piece with a pawn 
        # --- can't reproduce

        # problem - attacking lots of material seems to sway it too much, maybe focus on change in # of material attacked
        # --- Implemented, not tested

        # problem - should prefer capturing with pieces rather than pawns (maybe don't do this for all moves otherwise it will always openw ith knights)
        # --- Implemented, not tested

        # problem - if I put opponent in check, we shouldn't count any potential material loss other than moves that get them out of check
        # --- this is complicated, come back to it
        
        # problem - seen squares should look at ALL the squares my pieces see
        # --- Implemented, not tested
        
        # problem - attacker and defender logic to calculate material loss - needs to go through all captures
        # --- this is complicated, come back to it

        # problem - piece promotions should be calculated in terms of material gain/loss
        # problem - when a queen got promoted, capturing it was still evaluated to the same material gain of capturing a pawn

        # problem - stuff like squares seen, check, or attacking squares around the king doesn't matter if you're
        # about to lose the piece. It tends to do reckless sacrifices for this reason

        # Dangerous Check evaluation may be broken - it called a check dangerous when the piece could be captured.

        # "likely to be captures" could also use improvement. I 

        # in checking for attackers/defenders, the king should not count as a defender if doing so would put it in check
        # actually this might already be in place, need to look into it
