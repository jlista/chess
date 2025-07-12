import sys
from move import Move, Move_Type
from game_state import Game_State
from piece import Piece, Piece_Type
from typing import List
from utils import *

class MoveNode:
    state: Game_State
    sequence = []
    evaluation = 0
    children = []
    parent = None  
    resolved = False
    is_interesting = False
    line_continuation = None
    move = None

    def __init__(self, state,sequence,evaluation,parent,move):
        self.state = state
        self.sequence = sequence
        self.evaluation = evaluation
        self.parent = parent
        self.move = move

class Evaluator:

    def find_legal_moves(self, game_state, is_white):
        legal_moves = []
        for piece in game_state.pieces:
            if piece.is_white == is_white:
                candidates = game_state.potential_moves_from_square[piece.loc_rank][piece.loc_file]
                for candidate in candidates:
                    moves = []
                    if piece.piece_type == Piece_Type.PAWN:
                        if candidate[1] != piece.loc_file and game_state.board[candidate[0]][candidate[1]] is None:
                            moves = [Move(piece,candidate[0],candidate[1],Move_Type.EN_PASSANT)]
                        elif candidate[0] in [0,7]:
                            promote_to_queen = Move(piece,candidate[0],candidate[1],Move_Type.PROMOTE_PAWN)
                            promote_to_queen.promote_to = Piece_Type.QUEEN
                            promote_to_rook = Move(piece,candidate[0],candidate[1],Move_Type.PROMOTE_PAWN)
                            promote_to_rook.promote_to = Piece_Type.ROOK
                            promote_to_bishop = Move(piece,candidate[0],candidate[1],Move_Type.PROMOTE_PAWN)
                            promote_to_bishop.promote_to = Piece_Type.BISHOP
                            promote_to_knight = Move(piece,candidate[0],candidate[1],Move_Type.PROMOTE_PAWN)
                            promote_to_knight.promote_to = Piece_Type.KNIGHT
                            moves = [promote_to_queen,promote_to_bishop,promote_to_rook,promote_to_knight]
                        else:
                            moves = [Move(piece,candidate[0],candidate[1])]
                    else:
                        moves = [Move(piece,candidate[0],candidate[1])]
                    for move in moves:
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
        can_promote_pawn = move.piece.piece_type == Piece_Type.PAWN and move.dest_rank in (0,7)

        if move.move_type == Move_Type.CASTLE_KINGSIDE:
            return self.can_castle(game_state,move.is_white,True)
        if move.move_type == Move_Type.CASTLE_QUEENSIDE:
            return self.can_castle(game_state,move.is_white,False)
        if move.move_type == Move_Type.PROMOTE_PAWN and not can_promote_pawn:
            return False
        if can_promote_pawn and move.move_type != Move_Type.PROMOTE_PAWN:
            return False
        move_blocked = self.is_move_blocked(move,game_state)
        if not move_blocked:
            in_check = self.does_move_put_player_in_check(move,game_state)
            if not in_check:
                return True
        return False

    def is_move_blocked(self,move: Move,game_state: Game_State):
        
        occupant = game_state.board[move.dest_rank][move.dest_file]
        if occupant is None or (occupant.is_white != move.is_white and occupant.piece_type != Piece_Type.KING):
            return False
        return True

    def does_move_put_player_in_check(self,move: Move,game_state: Game_State):
        spoof_state = game_state.execute_hypothetical(move)
        move.game_state = spoof_state
        if move.is_white and spoof_state.is_white_in_check:
            return True
        if not move.is_white and spoof_state.is_black_in_check:
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


    move_tree = []
    def find_next_move(self, game_state, is_white):
        self.move_tree = [[MoveNode(game_state,[],0,None,None)]]

        MAX_DEPTH = 4

        for level in range(MAX_DEPTH):
            self.evaluate_move_tree(is_white,level)
            viable_moves = [move for move in self.move_tree[1] if not move.resolved]
            if len(viable_moves) == 1:
                break


        lowest_rating = sys.maxsize
        node_choice = None
        for node in self.move_tree[1]:
            if node.evaluation < lowest_rating:
                lowest_rating = node.evaluation
                node_choice = node

        return game_state.move_from_notation(node_choice.sequence[0],False)

    def mark_line_interesting(self,move):
        move.is_interesting = True
        if move.parent is not None:
            self.mark_line_interesting(move.parent)
    def resolve_branch(self,node):
        node.resolved = True
        for c in node.children:
            self.resolve_branch(c)

    def prune_uninteresting_moves(self, level, is_white):

        MIN_PER_LEVEL = 300
        MAX_PER_LEVEL = 400
        nodes = self.move_tree[level]
        interesting_nodes = []

        for node in nodes:

            node.is_interesting = False
            if abs(node.state.white_material - node.parent.state.white_material) > 1 or abs(node.state.black_material - node.parent.state.black_material) > 1:
                node.is_interesting = True
                self.mark_line_interesting(node)
            if node.state.is_white_in_check or node.state.is_black_in_check:
                node.is_interesting = True
                self.mark_line_interesting(node)
            if node.parent.state.is_white_in_check or node.parent.state.is_black_in_check: # forcing move/checkmate sequence 
                node.is_interesting = True
                self.mark_line_interesting(node)
            if abs(node.state.white_potential_losses - node.parent.state.white_potential_losses) > 3 or abs(node.state.black_potential_losses - node.parent.state.black_potential_losses) > 3:
                node.is_interesting = True
                self.mark_line_interesting(node)
            if node.is_interesting:
                interesting_nodes.append(node)

        num_marked_interesting = len(interesting_nodes)
        if num_marked_interesting < MIN_PER_LEVEL:
            sorted_nodes = sorted(nodes,key = lambda x: x.evaluation - x.parent.evaluation, reverse = is_white)
            i = 0
            while num_marked_interesting < MIN_PER_LEVEL and i < len(sorted_nodes):
                if not sorted_nodes[i].is_interesting:
                    sorted_nodes[i].is_interesting = True
                    self.mark_line_interesting(sorted_nodes[i]) 
                    num_marked_interesting += 1
                i=i+1 

        # this might not be a good heuristic - maybe need a way to judge how interesting a move is and remove the less interesting ones regardless of rating
        elif len(interesting_nodes) > MAX_PER_LEVEL:
            sorted_nodes = sorted(nodes,key = lambda x: x.evaluation - x.parent.evaluation, reverse = not is_white)
            i=0
            while num_marked_interesting > MAX_PER_LEVEL and i < len(sorted_nodes):
                if sorted_nodes[i].is_interesting:
                    sorted_nodes[i].is_interesting = False
                    num_marked_interesting -= 1
                i=i+1 

        for node in nodes:
            if not node.is_interesting:
                self.resolve_branch(node)

    def prune_bad_lines(self,level,is_white):
       
        if level == -1: return
        elif level == 0:
            pruning_levels = (1,2,1)
        elif level == 1:
            pruning_levels = (2,0,-1)
        else:
            pruning_levels = (level+1,0,-1)
        for pruning_level in range(*pruning_levels):

            if pruning_level == 1:
                threshold = 15
            elif pruning_level < 3:
                threshold = 15
            else:
                threshold = 15
            num_pruned = 0
            num_total = 0
            num_bad_interesting = 0
            parents = self.move_tree[pruning_level-1]
            for parent in [p for p in parents if not p.resolved]:
                
                nodes = parent.children
                nodes_sorted = sorted(nodes,key=lambda x: x.evaluation, reverse = is_white)
                best_so_far = nodes_sorted[0]
                for node in nodes:
                    if not node.resolved:
                        num_total += 1
                        if abs(best_so_far.evaluation - node.evaluation) > threshold:
                            if not node.is_interesting:
                                self.resolve_branch(node)
                                num_pruned += 1
                            elif pruning_level + 2 < len(self.move_tree):
                                num_bad_interesting += 1
                                self.resolve_branch(node)
                                num_pruned += 1

            is_white = not is_white



    def propogate_evaluations(self,level, is_white):
        for back_level in range(level,-1,-1):
            for node in self.move_tree[back_level]:

                if not node.resolved:
                    sorted_children = sorted(node.children, key=lambda x: x.evaluation)

                    if back_level % 2 == 1:
                        # for each player move, update its evaluation to that of the best child opponent move
                            if is_white: # if the player is white and we are looking at player moves, assume black will play the best (most negative) move
                                node.evaluation = sorted_children[0].evaluation
                                node.line_continuation = sorted_children[0]
                            else: # if the player is black and we are looking at player moves, assume white will play the best (most positive) move
                                node.evaluation = sorted_children[-1].evaluation
                                node.line_continuation = sorted_children[-1]
                    else:
                    # for each opponent move, update its evaluation to that of the best child player move
                        if is_white: # if the player is white and we are looking at opponent moves, assume white will play the best (most positive) move
                            node.evaluation = sorted_children[-1].evaluation
                            node.line_continuation = sorted_children[-1]
                        else: # if the player is black and we are looking at opponent moves, assume black will play the best (most negative) move
                            node.evaluation = sorted_children[0].evaluation
                            node.line_continuation = sorted_children[0]
                            

    def evaluate_move_tree(self,is_white,level):
        base_nodes = self.move_tree[level*2]

        player_choices = []
        opponent_choices = []

        for node in base_nodes:
            if not node.resolved:
                child_nodes = []
                possible_moves = self.find_legal_moves(node.state,is_white)
                if len(possible_moves) == 0:
                    node.resolved = True
                    if is_white and node.state.is_white_in_check:
                        node.evaluation = -1*sys.maxsize
                    elif not is_white and node.state.is_black_in_check:
                        node.evaluation = sys.maxsize
                    else:
                        node.evaluation = 0
                for move in possible_moves:
                    move.quality = self.rate_move_quality_heuristic(move,move.game_state)
                    child_nodes.append(MoveNode(move.game_state, node.sequence + [move.get_notation()], move.quality, node, move))
                node.children = child_nodes
                player_choices.extend(child_nodes)
        
        self.move_tree.append(player_choices)
        self.propogate_evaluations(level*2,is_white)
        self.prune_uninteresting_moves(level*2+1,is_white)

        self.prune_bad_lines(level*2 - 1, not is_white)

        for node in player_choices:
            if not node.resolved:
                child_nodes = []
                possible_moves = self.find_legal_moves(node.state,not is_white)

                if len(possible_moves) == 0:
                    node.resolved = True
                    if not is_white and node.state.is_white_in_check:
                        node.evaluation = -1*sys.maxsize
                    elif is_white and node.state.is_black_in_check:
                        node.evaluation = sys.maxsize
                    else:
                        node.evaluation = 0
                for move in possible_moves:
                    move.quality = self.rate_move_quality_heuristic(move,move.game_state)
                    child_nodes.append(MoveNode(move.game_state, node.sequence + [move.get_notation()], move.quality, node, move))

                node.children = child_nodes
                opponent_choices.extend(child_nodes)

        self.move_tree.append(opponent_choices)
        self.propogate_evaluations(level*2+1,is_white)

        self.prune_uninteresting_moves(level*2+2,not is_white)
        self.prune_bad_lines(level*2, is_white)
        # prune bad or uninteresting moves

    lines = [[],[]]
    def find_lines(self,line,game_state,depth,is_white):

        legal_moves = self.find_legal_moves(game_state,is_white)
        for move in legal_moves:
            spoof_state: Game_State = move.game_state
            move.quality = self.rate_move_quality_heuristic(move,spoof_state)
            
            newline = [move]
            responses = self.find_legal_moves(spoof_state, not is_white)
            best_response_q = -999999999999
            best_response = None
            for response in responses:
                spoof_state2: Game_State = response.game_state
                response.quality = self.rate_move_quality_heuristic(response,spoof_state2)
                if response.quality > best_response_q:
                    best_response_q = response.quality
                    best_response = response
            self.lines[depth].append(line + newline + [best_response])

        self.lines[depth] = sorted(self.lines[depth], key = lambda x: x[-1].quality)
        if depth == 0:
            return

        candidates = self.lines[depth][0:5]
        for candidate in candidates:
            return self.find_lines(candidate,candidate[-1].game_state,depth-1,is_white)

    def find_top_moves(self, game_state, is_white):
        self.lines = [[],[]]
        self.find_lines([],game_state,1,is_white)
        return self.lines

    
    def rate_move_quality_heuristic(self,move,spoof_state: Game_State):
        
        ## TODO
        """
        Positions must be evaluated based on whose turn it is. If you have a hanging piece but it's your turn,
        this is not bad since you can just move it. But if it's the opponent's turn then you have a problem. 
        """

        white_pieces = spoof_state.white_pieces
        black_pieces = spoof_state.black_pieces
        white_king = spoof_state.white_king
        black_king = spoof_state.black_king

        # Count material
        white_material = spoof_state.white_material
        black_material = spoof_state.black_material

        white_attackers_by_square = [[[] for r in range(8)] for f in range(8)]
        black_attackers_by_square = [[[] for r in range(8)] for f in range(8)]
        for p in white_pieces:
            for sq in spoof_state.seen_by_square[p.loc_rank][p.loc_file]:
                white_attackers_by_square[sq[0]][sq[1]].append(p)
        for p in black_pieces:
            for sq in spoof_state.seen_by_square[p.loc_rank][p.loc_file]:
                black_attackers_by_square[sq[0]][sq[1]].append(p)

        # TODO: this is still broken because when calculating for white, we haven't yet removed the black kings so it will think it can attack those squares if two kings are facing
        for rank in range(8):
            for file in range(8):
                for white_attacker in white_attackers_by_square[rank][file]:
                    if white_attacker.piece_type == Piece_Type.KING and len(black_attackers_by_square[rank][file]) > 0:
                        white_attackers_by_square[rank][file].remove(white_attacker)
                for black_attacker in black_attackers_by_square[rank][file]:
                    if black_attacker.piece_type == Piece_Type.KING and len(white_attackers_by_square[rank][file]) > 0:
                        black_attackers_by_square[rank][file].remove(black_attacker)

        black_squares_seen = 0
        white_squares_seen = 0

        for rank in range(8):
            for file in range(8):
                if len(white_attackers_by_square[rank][file]) > 0:
                    white_squares_seen += 1
                if len(black_attackers_by_square[rank][file]) > 0:
                    white_squares_seen += 1

        # Count seen critical squares
        central_squares = [(3,3),(3,4),(4,3),(4,4)]
        white_king_adjacent_squares = spoof_state.seen_by_square[white_king.loc_rank][white_king.loc_file]
        black_king_adjacent_squares = spoof_state.seen_by_square[black_king.loc_rank][black_king.loc_file]
        white_critical_squares = central_squares + black_king_adjacent_squares
        black_critical_squares = central_squares + white_king_adjacent_squares

        white_seen_critical_squares = 0
        black_seen_critical_squares = 0

        for cr_rank,cr_file in white_critical_squares:
            if len(white_attackers_by_square[cr_rank][cr_file]) > 0:
                white_seen_critical_squares += 1
    
        for cr_rank,cr_file in black_critical_squares:
            if len(black_attackers_by_square[cr_rank][cr_file]) > 0:
                black_seen_critical_squares += 1

        # Count defenders
        white_defenders = sum([len(white_attackers_by_square[p.loc_rank][p.loc_file]) for p in white_pieces])
        black_defenders = sum([len(black_attackers_by_square[p.loc_rank][p.loc_file]) for p in black_pieces])

        # Count attackers
        white_attackers = sum([len(white_attackers_by_square[p.loc_rank][p.loc_file]) for p in black_pieces])
        black_attackers = sum([len(black_attackers_by_square[p.loc_rank][p.loc_file]) for p in white_pieces])


        # Count potential material losses
        white_potential_losses = 0
        white_escapable_pieces = [] # TODO: currently only checks if it can move to a safe square. Also need to look for blocks
        white_trapped_pieces = []
        for p in [p for p in white_pieces if p.piece_type is not Piece_Type.KING]:
            loss = 0
            piece_attackers = black_attackers_by_square[p.loc_rank][p.loc_file]
            if len(piece_attackers) > 0:


                # TODO: this is WRONG because get_potential_moves counts occupied squares, even if it's occupied by your own pieces
                safe_squares = [sq for sq in spoof_state.potential_moves_from_square[p.loc_rank][p.loc_file] if len(black_attackers_by_square[sq[0]][sq[1]]) == 0]

                piece_defenders = white_attackers_by_square[p.loc_rank][p.loc_file]
                weakest_attacker = sorted(piece_attackers, key=lambda x: x.value)[0]
                if len(piece_defenders) == 0: # TODO: need to add logic to see if using defender would be legal (pin or defender is king)
                    loss = p.value
                elif weakest_attacker.value < p.value:
                    loss = p.value - weakest_attacker.value
                    
                if not move.piece.is_white and len(safe_squares) > 0:
                    white_escapable_pieces.append((p, loss))
                else:
                    white_trapped_pieces.append((p,loss))

        if len(white_trapped_pieces) > 0:
            white_worst_loss_trapped = max([p[1] for p in white_trapped_pieces])
            if len(white_escapable_pieces) < 2:
                white_potential_losses = white_worst_loss_trapped
            else:
                white_escapable_pieces = sorted(white_escapable_pieces, key=lambda x: x[1])
                white_potential_losses = max(white_worst_loss_trapped, white_escapable_pieces[-2][1])

        black_potential_losses = 0
        black_escapable_pieces = []
        black_trapped_pieces = []
        for p in [p for p in black_pieces if p.piece_type is not Piece_Type.KING]:
            loss = 0
            piece_attackers = white_attackers_by_square[p.loc_rank][p.loc_file]
            if len(piece_attackers) > 0:

                safe_squares = [sq for sq in spoof_state.potential_moves_from_square[p.loc_rank][p.loc_file] if len(white_attackers_by_square[sq[0]][sq[1]]) == 0]

                piece_defenders = black_attackers_by_square[p.loc_rank][p.loc_file]
                weakest_attacker = sorted(piece_attackers, key=lambda x: x.value)[0]
                if len(piece_defenders) == 0: # TODO: add logic to see if using defender would be legal (pin or defender is king)
                    loss = p.value
                elif weakest_attacker.value < p.value:
                    loss = p.value - weakest_attacker.value
                    
                if move.piece.is_white and len(safe_squares) > 0:
                    black_escapable_pieces.append((p, loss))
                else:
                    black_trapped_pieces.append((p,loss))

        if black_trapped_pieces:
            black_worst_loss_trapped = max([p[1] for p in black_trapped_pieces])
            if len(black_escapable_pieces) < 2:
                black_potential_losses = black_worst_loss_trapped
            else:
                black_escapable_pieces = sorted(black_escapable_pieces, key=lambda x: x[1])
                black_potential_losses = max(black_worst_loss_trapped, black_escapable_pieces[-1][1])
        spoof_state.white_potential_losses = white_potential_losses
        spoof_state.black_potential_losses = black_potential_losses

        # TODO - move potential losses calculation to the state

        material_score = 20 * (white_material - black_material)
        move.metadata += f"Material: {material_score} "
        loss_score = 20 * (black_potential_losses - white_potential_losses)
        move.metadata += f"Potential loss: {loss_score}"
        seen_score = white_squares_seen - black_squares_seen
        move.metadata += f"Seen: {seen_score} "
        critical_seen_score = 4 * (white_seen_critical_squares - black_seen_critical_squares)
        move.metadata += f"Critical: {critical_seen_score} "
        defender_score = 1 * (white_defenders - black_defenders)
        move.metadata += f"Defenders: {defender_score} "
        attacker_score = 1 * (white_attackers - black_attackers)
        move.metadata += f"Attackers: {attacker_score} "

        quality = material_score + loss_score + seen_score + critical_seen_score + defender_score + attacker_score
        
        return quality
