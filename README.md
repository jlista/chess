This is a basic chess engine which is entirely heuristic-based (no neural networks). It is slow and not very strong but should be able to beat a novice human player. Usage is based on a modified form of chess notation.

NOTATION RULES:

The notation used by this engine differs from standard chess notation.

* the type of piece that is moving must always be indicated, even if it is a pawn (P is used to indicate pawn)
* the file that the piece is on must always be indicated, even if it is unambiguous
* capturing is implied, not indicated

Examples:

Pe-e5 moves the e pawn to e5
Qa-b4 moves the queen to b4
Nb-c3 moves the knight on the b file to c3
Pa-b3 moves the a pawn to b3, capturing a piece (note that there is no "x" marking a capture)
Pa-b6 moves the a pawn to b6, capturing a pawn on b5 en passant (assuming this is a legal move)
O-O castles kingside
O-O-O castles queenside
Pa-a8=Q moves the a pawn to a8, promoting to queen 

Game representation:

The state of the board will be shown in a diagram like this:

\\---------------------------------------
\\R'|  N'|  B'|  Q'|  K'|  B'|  N'|  R'|
\\--------------------------------------
\\P'|  P'|  P'|  P'|  P'|  P'|  P'|  P'|
\\---------------------------------------
\\   |    |    |    |    |    |    |    |
\\---------------------------------------
\\   |    |    |    |    |    |    |    |
\\---------------------------------------
\\   |    |    |    |    |    |    |    |
\\---------------------------------------
\\   |    |    |    |    |    |    |    |
\\---------------------------------------
\\ P |  P |  P |  P |  P |  P |  P |  P |
\\---------------------------------------
\\ R |  N |  B |  Q |  K |  B |  N |  R |

The apostrophes represent the black pieces. A new board will be printed after each move showing the state of the game.

USAGE:

Run the file chess.py in Python
The first prompt allows you to enter a starting state. This will be in the form of an array listing a sequence of moves leading to the starting state. For example:

["Pe-e4", "Pe-e5"]

will initialize the game with these two moves already made. This allows you to start playing from any position. If you want to start playing from the default position, just hit enter to skip this prompt.

Next, you will be prompted to enter a move. Enter your move using the notation described above. If the notation is invalid or the move is illegal, you will be prompted to enter a different move. Otherwise, the move will be made and the computer will then make its move. Note that this can sometimes take a while as the engine is slow. After the game state is printed, the current sequence of moves will also be printed, so the output will look something like this:

---------------------------------------
 R'|  N'|  B'|  Q'|  K'|  B'|    |  R'|
---------------------------------------
 P'|  P'|  P'|  P'|  P'|  P'|  P'|  P'|
---------------------------------------
   |    |    |    |    |  N'|    |    |
---------------------------------------
   |    |    |    |    |    |    |    |
---------------------------------------
   |    |    |    |  P |    |    |    |
---------------------------------------
   |    |    |    |    |    |    |    |
---------------------------------------
 P |  P |  P |  P |    |  P |  P |  P |
---------------------------------------
 R |  N |  B |  Q |  K |  B |  N |  R |
['Pe-e4', 'Ng-f6']

The string underneath the board shows the current sequence of moves. You can copy this and save it somewhere in order to exit and resume the game later.
