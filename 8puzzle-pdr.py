import time
import heapq
import tkinter as tk
from tkinter import filedialog
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

# Interface gráfica
class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver")
        self.board = []
        self.buttons = []
        self.size = 3
        self.load_button = tk.Button(root, text="Carregar Arquivo", command=self.load_puzzle)
        self.load_button.pack()
        self.solve_button = tk.Button(root, text="Resolver", command=self.solve_puzzle, state=tk.DISABLED)
        self.solve_button.pack()
        self.frame = tk.Frame(root)
        self.frame.pack()
        
    def load_puzzle(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        
        with open(file_path, 'r') as file:
            self.board = file.readline().strip().split()
        
        self.size = int(len(self.board) ** 0.5)
        self.create_board()
        self.solve_button.config(state=tk.NORMAL)
    
    def create_board(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        self.buttons = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                text = self.board[i * self.size + j]
                btn = tk.Button(self.frame, text=text, font=("Arial", 18), width=4, height=2)
                btn.grid(row=i, column=j)
                row.append(btn)
            self.buttons.append(row)
    
    def update_board(self, board):
        for i in range(self.size):
            for j in range(self.size):
                self.buttons[i][j].config(text=board[i * self.size + j])
        self.root.update()
        time.sleep(0.5)
    
    def solve_puzzle(self):
        initial_state = PuzzleState(self.board)
        goal = [str(i) for i in range(1, self.size * self.size)] + ['X']
        solution, _, _, _ = a_star(initial_state, goal, self.size)
        
        if solution:
            path = reconstruct_path(solution)
            for state in path:
                self.update_board(state.board)

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()
