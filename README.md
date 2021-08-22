A python implementation of the popular board game Connect Four.

A Game class handles the flow of the game, while a position class allows to handle the current position and explore its potential developments. A simple AI uses minimax search with alpha-beta pruning to output a move given as input a position.

Potential foreseen improvements:
  1. use a more efficient representation for the board state. Currently it is a matrix of dimension 6 x 7, each entry storing a number representing the state of the corresponding      square on the board. It could be made more efficient by using a binary representation as a string of 7 x 7 bits, each group of 7 representing the state of a single column          (the last 1 in the substring indicates the first empty square from below, and below that 1's represent current player's stones, 0's other's stones).
  2. create a lookup table where to store the score of the positions that have already been explored (since they are far too many, a criterion to decide which to keep is also          needed, a simple one being the last few explored).
  3. hand-engineer a static evaluation of the board state that can guide the AI when maximum depth has been reached.
