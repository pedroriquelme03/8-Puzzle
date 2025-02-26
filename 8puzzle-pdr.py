import time
import heapq
from collections import deque
import tracemalloc

# Classe para representar o estado do jogo
class PuzzleState:
    def __init__(self, board, parent=None, move=None, depth=0, cost=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
        self.cost = cost
        self.blank_pos = board.index('X')

    def __lt__(self, other):
        return (self.depth + self.cost) < (other.depth + other.cost)

    def get_moves(self, size):
        moves = []
        row, col = divmod(self.blank_pos, size)
        directions = {'Up': -size, 'Down': size, 'Left': -1, 'Right': 1}

        for move, delta in directions.items():
            new_pos = self.blank_pos + delta
            if 0 <= new_pos < size * size:
                if (move == 'Left' and col == 0) or (move == 'Right' and col == size - 1):
                    continue
                new_board = self.board[:]
                new_board[self.blank_pos], new_board[new_pos] = new_board[new_pos], new_board[self.blank_pos]
                moves.append(PuzzleState(new_board, self, move, self.depth + 1, self.cost))

        return moves

# Função heurística: número de peças fora do lugar
def heuristic(state, goal):
    return sum(1 for i in range(len(state.board)) if state.board[i] != goal[i] and state.board[i] != 'X')

# Busca A* (A estrela)
def a_star(initial, goal, size):
    start_time = time.time()
    tracemalloc.start()
    pq = []
    heapq.heappush(pq, (0, initial))
    visited = set()
    nodes_visited = 0

    while pq:
        _, state = heapq.heappop(pq)
        nodes_visited += 1

        if state.board == goal:
            memory_used = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            return state, nodes_visited, time.time() - start_time, memory_used

        visited.add(tuple(state.board))
        for move in state.get_moves(size):
            if tuple(move.board) not in visited:
                move.cost = heuristic(move, goal)
                heapq.heappush(pq, (move.depth + move.cost, move))

    return None, nodes_visited, time.time() - start_time, tracemalloc.get_traced_memory()[1]

# Função para reconstruir o caminho da solução
def reconstruct_path(state):
    path = []
    while state:
        path.append(state)
        state = state.parent
    return path[::-1]

# Função para exibir o tabuleiro no terminal
def print_board(state, size):
    for i in range(size):
        print(" ".join(state.board[i * size:(i + 1) * size]))
    print("-" * (size * 2))

# Função principal
def solve_puzzle(filename):
    with open(filename, 'r') as file:
        board = file.readline().strip().split()

    size = int(len(board) ** 0.5)
    goal = [str(i) for i in range(1, size * size)] + ['X']
    initial_state = PuzzleState(board)

    print("🔍 Resolvendo o 8-Puzzle com A*...\n")

    solution, nodes, elapsed_time, memory_used = a_star(initial_state, goal, size)

    if solution:
        path = reconstruct_path(solution)
        for state in path:
            print_board(state, size)
            time.sleep(0.5)  # Adiciona um pequeno delay para visualizar a solução passo a passo

        print(f"\n✅ Solução encontrada!\nNós visitados: {nodes}")
        print(f"Tempo de execução: {elapsed_time:.4f}s")
        print(f"Memória utilizada: {memory_used / 1024:.2f} KB")

    else:
        print("❌ Nenhuma solução encontrada.")

# Executar a solução com um arquivo de entrada
solve_puzzle("input.txt")
