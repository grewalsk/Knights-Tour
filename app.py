import sys
import time

# Define KNIGHT_MOVES at the module level for accessibility by helper functions
KNIGHT_MOVES = [
    (-2, -1), (-2, 1), (-1, -2), (-1, 2),
    (1, -2), (1, 2), (2, -1), (2, 1)
]

def initial_degrees(m, n):
    """
    Calculates the initial degree for each square on an m x n board.
    The degree is the number of possible knight moves from that square,
    assuming all other squares are unvisited.
    """
    degree_board = [[0 for _ in range(n)] for _ in range(m)]
    for r_idx in range(m):
        for c_idx in range(n):
            count = 0
            for dr, dc in KNIGHT_MOVES:
                nr, nc = r_idx + dr, c_idx + dc
                if 0 <= nr < m and 0 <= nc < n:
                    count += 1
            degree_board[r_idx][c_idx] = count
    return degree_board

def update_degrees_on_visit_change(changed_r, changed_c, m, n, degree_board, delta):
    """
    Updates degrees of neighbors of (changed_r, changed_c) when its visited status changes.
    'degree_board[x][y]' stores how many unvisited squares (x,y) can move to.
    delta = -1 if (changed_r, changed_c) just became visited (it's one less
             unvisited option for its neighbors).
    delta = +1 if (changed_r, changed_c) just became unvisited (it's one more
             unvisited option for its neighbors).
    """
    for dr, dc in KNIGHT_MOVES:
        nr, nc = changed_r + dr, changed_c + dc
        # Check if the neighbor (nr, nc) is on the board
        if 0 <= nr < m and 0 <= nc < n:
            degree_board[nr][nc] += delta

def get_warnsdorff_move(curr_r, curr_c, m, n, board, degree_board):
    """
    Finds the next move using Warnsdorff's heuristic with specified tie-breaking.
    1. Chooses an unvisited neighbour with the minimal current degree (fewest onward moves).
    2. Tie-break: Chooses the candidate whose own minimal-degree successor is smallest.
    3. Tie-break (if still tied): Picks lexicographically (row, col).
    Returns (next_r, next_c) or None if no move is possible.
    """
    potential_next_squares = [] 
    for dr, dc in KNIGHT_MOVES:
        nr, nc = curr_r + dr, curr_c + dc
        if 0 <= nr < m and 0 <= nc < n and board[nr][nc] == 0: # Valid & unvisited
            # degree_board[nr][nc] is the number of unvisited moves from (nr, nc)
            potential_next_squares.append((degree_board[nr][nc], nr, nc))

    if not potential_next_squares:
        return None

    # Sort by degree (Warnsdorff), then row, then col (for initial tie-breaking)
    potential_next_squares.sort() 
    
    min_degree_val = potential_next_squares[0][0]
    
    # Filter candidates with the minimal degree
    candidates_min_degree = [sq for sq in potential_next_squares if sq[0] == min_degree_val]

    if len(candidates_min_degree) == 1:
        # (degree, r, c) -> return (r, c)
        return candidates_min_degree[0][1], candidates_min_degree[0][2]

    # Tie-breaking 1: Minimal-degree successor
    candidates_with_succ_info = []
    for _, cand_r, cand_c in candidates_min_degree: 
        min_succ_deg_for_this_cand = float('inf')
        has_unvisited_successors = False
        for dr_s, dc_s in KNIGHT_MOVES: # Successors of (cand_r, cand_c)
            succ_r, succ_c = cand_r + dr_s, cand_c + dc_s
            if 0 <= succ_r < m and 0 <= succ_c < n and board[succ_r][succ_c] == 0:
                has_unvisited_successors = True
                min_succ_deg_for_this_cand = min(min_succ_deg_for_this_cand, 
                                                 degree_board[succ_r][succ_c])
        
        actual_min_succ_deg = min_succ_deg_for_this_cand if has_unvisited_successors else float('inf')
        candidates_with_succ_info.append((actual_min_succ_deg, cand_r, cand_c))

    # Sort by (min_successor_degree, candidate_r, candidate_c)
    # This automatically handles the final lexicographical tie-break.
    candidates_with_succ_info.sort() 
    
    return candidates_with_succ_info[0][1], candidates_with_succ_info[0][2]


def find_knights_tour(m_rows, n_cols, k_backtrack_limit, start_r, start_c):
    """
    Attempts to find a Knight's Tour on an m_rows x n_cols chessboard.
    Uses Warnsdorff's heuristic with backtracking limited to k_backtrack_limit total undos.
    Returns the tour as a list of (r, c) tuples, or None if impossible.
    """
    # board[r][c] = 0 if unvisited, otherwise stores the move number (1 to m*n)
    board = [[0 for _ in range(n_cols)] for _ in range(m_rows)]
    # degree_board[r][c] = number of unvisited squares reachable from (r,c)
    degree_board = initial_degrees(m_rows, n_cols)
    
    tour_path = []  # Stores (r, c) tuples of the tour
    curr_r, curr_c = start_r, start_c
    num_visited_squares = 0
    backtracks_performed = 0

    # Process the starting square
    num_visited_squares += 1
    board[curr_r][curr_c] = num_visited_squares
    tour_path.append((curr_r, curr_c))
    update_degrees_on_visit_change(curr_r, curr_c, m_rows, n_cols, degree_board, -1)

    target_visited_squares = m_rows * n_cols
    while num_visited_squares < target_visited_squares:
        next_move_coords = get_warnsdorff_move(curr_r, curr_c, m_rows, n_cols, board, degree_board)

        if next_move_coords:
            curr_r, curr_c = next_move_coords
            num_visited_squares += 1
            board[curr_r][curr_c] = num_visited_squares
            tour_path.append((curr_r, curr_c))
            update_degrees_on_visit_change(curr_r, curr_c, m_rows, n_cols, degree_board, -1)
        else:  # Stuck: No valid unvisited neighbor from current square
            if backtracks_performed >= k_backtrack_limit or len(tour_path) <= 1:
                # Max backtracks used or cannot backtrack from start square
                return None 

            backtracks_performed += 1
            
            # Unvisit the last square added to the tour path
            square_to_unvisit_r, square_to_unvisit_c = tour_path.pop()
            board[square_to_unvisit_r][square_to_unvisit_c] = 0
            num_visited_squares -= 1

            # Update degrees as this square is now unvisited
            update_degrees_on_visit_change(square_to_unvisit_r, square_to_unvisit_c, 
                                           m_rows, n_cols, degree_board, +1)
            
            # Set current position to the new end of tour_path
            curr_r, curr_c = tour_path[-1]
            # Loop continues, will try to find a new move from this (now current) square

    if num_visited_squares == target_visited_squares:
        return tour_path # Tour complete
    
    return None # Should generally be caught by backtrack limit or completion

def run_demo_test(m, n, k, r_start, c_start, test_id_str):
    """Runs a specific test case for the --demo mode and prints summary."""
    print(f"Running test: {test_id_str} ({m}x{n}, k={k}, start=({r_start},{c_start}))")
    
    start_time = time.perf_counter()
    tour = find_knights_tour(m, n, k, r_start, c_start)
    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000

    result_status = "SUCCESS" if tour else "IMPOSSIBLE"
    # Per spec, demo prints runtime. Adding result status for clarity.
    print(f"Result: {result_status}") 
    print(f"Runtime: {duration_ms:.2f} ms\n")

def main():
    """Handles command-line arguments, input, and output for the Knight's Tour."""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        # Using 'python knights_tour.py' as per problem example for --demo
        print("Usage: python knights_tour.py")
        print("Reads m n k (board dimensions, backtrack limit) from standard input.")
        print("Then reads r c (0-based start coordinates) from standard input.")
        print("\nExample input format (provide via stdin):")
        print("8 8 0")
        print("0 0")
        print("\nFlags:")
        print("  --demo    Run three canned test cases and print their results and runtimes.")
        print("  -h, --help Show this help message and exit.")
        return

    if "--demo" in args:
        print("Running demo tests...\n")
        run_demo_test(8, 8, 0, 0, 0, "Classic greedy, no backtracking")
        run_demo_test(8, 8, 10, 3, 4, "Small backtracking")
        run_demo_test(6, 5, 50, 2, 2, "Larger k")
        return

    try:
        line1 = sys.stdin.readline()
        m_rows, n_cols, k_limit = map(int, line1.split())
        line2 = sys.stdin.readline()
        start_r, start_c = map(int, line2.split())
    except ValueError:
        print("ERROR: Invalid input format. Expected 'm n k' on line 1, 'r c' on line 2.", file=sys.stderr)
        sys.exit(1)
    except EOFError: 
        print("ERROR: EOFError. Input stream ended prematurely. Expected two lines of input.", file=sys.stderr)
        sys.exit(1)

    # Validate inputs based on problem statement constraints
    if not (5 <= m_rows <= 500 and 5 <= n_cols <= 500):
        print(f"ERROR: Board dimensions m, n must be between 5 and 500. Got m={m_rows}, n={n_cols}", file=sys.stderr)
        sys.exit(1)
    if not (0 <= k_limit <= m_rows * n_cols):
        print(f"ERROR: Backtrack limit k must be between 0 and m*n ({m_rows*n_cols}). Got k={k_limit}", file=sys.stderr)
        sys.exit(1)
    if not (0 <= start_r < m_rows and 0 <= start_c < n_cols):
        print(f"ERROR: Start coordinates ({start_r},{start_c}) out of bounds for {m_rows}x{n_cols} board.", file=sys.stderr)
        sys.exit(1)
    
    tour_result = find_knights_tour(m_rows, n_cols, k_limit, start_r, start_c)

    if tour_result:
        print("SUCCESS")
        for r_move, c_move in tour_result:
            print(f"{r_move} {c_move}")
    else:
        print("IMPOSSIBLE")

if __name__ == "__main__":
    main()