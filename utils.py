def get_castling_coordinates(is_kingside,is_white):
    if is_kingside:
        if is_white:
            rook_start = (0,7)
            king_start = (0,4)
            rook_dest = (0,5)
            king_dest = (0,6)
            gap = None
        else:
            rook_start = (7,7)
            king_start = (7,4)
            rook_dest = (7,5)
            king_dest = (7,6)
            gap = None
        return rook_start,rook_dest,king_start,king_dest,gap
    else:
        if is_white:
            rook_start = (0,0)
            king_start = (0,4)
            rook_dest = (0,3)
            king_dest = (0,2)
            gap = (0,1)
        else:
            rook_start = (7,0)
            king_start = (7,4)
            rook_dest = (7,3)
            king_dest = (7,2)
            gap = (7,1)
        return rook_start,rook_dest,king_start,king_dest,gap

def letter_to_number(l):

        """
        returns a=1, b=2, etc. for both upper and lowercase
        """
        return ord(l) - 97