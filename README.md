# Knight's Tour Solver

This program finds a Knight's Tour on an `m x n` chessboard using Warnsdorff's heuristic with bounded backtracking.

## Problem Definition

The Knight's Tour problem seeks a sequence of moves by a knight on a chessboard such that the knight visits every square exactly once. If the tour ends on a square that is one knight's move from the starting square, it is a "closed" tour; otherwise, it is an "open" tour. This program finds an open tour.

Mathematically, this can be viewed as finding a **Hamiltonian path** in the "knight's graph," where:
*   **Vertices:** Each square `(r, c)` on the `m x n` board is a vertex.
*   **Edges:** An edge exists between two vertices (squares) if a knight can legally move from one to the other.

## Core Algorithm: Warnsdorff's Heuristic with Bounded Backtracking

The algorithm combines a greedy approach (Warnsdorff's rule) with a limited corrective mechanism (bounded backtracking).

### 1. Knight's Moves

The fundamental movement of the knight is defined by eight possible offsets `(dr, dc)` from a current square `(r, c)` to a new square `(r+dr, c+dc)`:
`{(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)}`

### 2. Warnsdorff's Heuristic for Move Selection

Warnsdorff's rule is a greedy heuristic used to choose the next move. At each step, the knight moves to an unvisited square that has the *fewest onward moves*.

*   **Degree of a Square:** The "degree" of a square `(r, c)` at any point in the tour is defined as the number of unvisited squares reachable by a knight's move from `(r, c)`.
    Let `V_u` be the set of unvisited squares. For a square `s = (r, c)`, let `N(s)` be the set of all squares reachable by a knight from `s`. The dynamic degree `d(s)` is `|{s' ∈ N(s) | s' ∈ V_u}|`.
*   **Move Choice:** From the current square, consider all reachable unvisited neighbors. Select the neighbor `s_next` that has the minimum `d(s_next)`.

### 3. Tie-Breaking Rules (Applied Sequentially)

If multiple potential next moves have the same minimal degree according to Warnsdorff's rule, the following tie-breaking rules are applied:

1.  **Minimal-Degree Successor:**
    *   For each tied candidate square `s_candidate`, examine its own unvisited successors (squares reachable by a knight from `s_candidate`).
    *   Find the minimum degree among these successors: `min_succ_deg(s_candidate) = min {d(s_successor)}` for all unvisited `s_successor ∈ N(s_candidate)`.
    *   If a candidate has no unvisited successors, its `min_succ_deg` can be considered infinite for comparison.
    *   The candidate square with the smallest `min_succ_deg` is chosen.

2.  **Lexicographical Order:**
    *   If a tie still persists after the minimal-degree successor rule, the candidate square `(r, c)` is chosen based on lexicographical order:
        *   Minimize `r` (row index).
        *   If `r` is still tied, minimize `c` (column index).

### 4. Bounded Backtracking

If the Warnsdorff's heuristic (with tie-breaking) leads to a state where no unvisited squares are reachable from the current square (a "dead end"), the algorithm can backtrack.

*   **Mechanism:** The last move made is undone. The knight returns to the previous square, and the square it just left is marked as unvisited again. Crucially, the degrees of the neighbors of the now-unvisited square are updated (incremented).
*   **Bound `k`:** The total number of such "undo" operations (backtracks) is limited by the input parameter `k`. If `k` backtracks have been performed and the algorithm is still stuck, it declares failure (IMPOSSIBLE).
*   The tour path is maintained as a list (acting as a stack), where the last `k` entries are implicitly the window for potential backtracking, though the limit `k` applies to the total count of pops/undos.

### 5. Termination

*   **Success:** The tour is successful if all `m x n` squares on the board have been visited.
*   **Failure:** The tour is declared IMPOSSIBLE if the algorithm reaches a dead end and the bounded backtracking limit `k` has been exhausted, or if it cannot backtrack further (e.g., from the starting square with no prior moves).

## Data Structures

1.  **Visited Array (`board[m][n]`):**
    *   An `m x n` integer matrix.
    *   `board[r][c] = 0` if the square `(r, c)` is unvisited.
    *   `board[r][c] = move_number` (from 1 to `m x n`) if visited, indicating the step at which it was visited.

2.  **Degree Array (`degree[m][n]`):**
    *   An `m x n` integer matrix.
    *   `degree[r][c]` stores the current number of unvisited squares reachable by a knight from square `(r, c)`.
    *   **Dynamic Updates:**
        *   When a square `(x, y)` is visited: For each neighbor `(nx, ny)` of `(x, y)`, `degree[nx][ny]` is decremented by 1.
        *   When a square `(x, y)` is unvisited (due to backtracking): For each neighbor `(nx, ny)` of `(x, y)`, `degree[nx][ny]` is incremented by 1.
        This allows O(1) lookup for degrees and O(1) update relative to the board size (specifically O(8) operations) when a square's status changes.

3.  **Tour Path (`tour_path`):**
    *   A list of `(r, c)` tuples, storing the sequence of squares visited in order. This list also serves as a stack for backtracking.

## Complexity Targets (as per prompt)

*   **Average-Case Time Complexity:** O(m × n)
    *   Each of the `m x n` squares is visited once.
    *   Selecting the next move using Warnsdorff's (including tie-breaking) involves checking at most 8 neighbors and then potentially 8 successors for each of those, resulting in a constant number of operations (roughly 8 + 8*8 = 72 in a complex tie-break).
    *   Updating degrees affects at most 8 neighboring squares.
    *   Thus, each step is effectively O(1) with respect to board size.

*   **Worst-Case Time Complexity (Backtracking Overhead):** O(k × 8) extra work for backtracking.
    *   Each backtrack operation involves popping from the tour, and updating degrees for up to 8 neighbors of the square being un-visited.
    *   The main loop still aims for `m x n` steps, but `k` such backtrack operations can add to the total operations.

*   **Memory Complexity:** O(m × n)
    *   Primarily for the `board` array (visited status) and the `degree` array.
    *   The `tour_path` also stores up to `m x n` coordinates.

## Input Parameters

*   `m, n`: Integers representing the board dimensions (rows, columns), `5 ≤ m, n ≤ 500`.
*   `k`: Integer representing the maximum number of moves that may be undone (backtrack limit), `0 ≤ k ≤ m × n`.
*   `r, c`: Integers representing the 0-based starting square coordinates, `0 ≤ r < m`, `0 ≤ c < n`.

## How to Run

1.  Save the code as `app.py` (or your chosen filename).
2.  Run from the terminal: `python app.py`
3.  The program will wait for input:
    *   Enter `m n k` (e.g., `8 8 0`) and press Enter.
    *   Enter `r c` (e.g., `0 0`) and press Enter.
4.  Alternatively, use the `--demo` flag to run canned tests: `python app.py --demo`
5.  Use `-h` or `--help` for a usage message: `python app.py --help`

---