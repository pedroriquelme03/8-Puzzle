import time
import tkinter as tk
from collections import deque
import tracemalloc

# Classe para representar o estado do jogo
class PuzzleState:
    def __init__(self, board, parent=None, move=None, depth=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
        self.blank_pos = board.index('X')
    
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
                moves.append(PuzzleState(new_board, self, move, self.depth + 1))
        
        return moves

# Busca em Profundidade (DFS)
def dfs(initial, goal, size, log_callback):
    start_time = time.time()
    tracemalloc.start()
    stack = [initial]
    visited = set()
    nodes_visited = 0
    
    while stack:
        state = stack.pop()
        nodes_visited += 1
        log_callback(f"Nó visitado: {nodes_visited}, Profundidade: {state.depth}")
        
        if state.board == goal:
            memory_used = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            return state, nodes_visited, time.time() - start_time, memory_used
        
        visited.add(tuple(state.board))
        for move in reversed(state.get_moves(size)):
            if tuple(move.board) not in visited:
                stack.append(move)
    
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
        self.root.title("8-Puzzle Solver - DFS")
        self.root.geometry("500x500")  # Tamanho fixo
        
        self.frame = tk.Frame(root, width=250, height=250)
        self.frame.grid(row=0, column=0, padx=10, pady=10)
        
        self.log_text = tk.Text(root, height=20, width=30)
        self.log_text.grid(row=0, column=1, padx=10, pady=10)
        
        self.board = []
        self.buttons = []
        self.size = 3
        self.load_puzzle()
        
        self.solve_button = tk.Button(root, text="Resolver (DFS)", command=self.solve_puzzle)
        self.solve_button.grid(row=1, column=0, pady=10)
    
    def load_puzzle(self):
        with open("input.txt", 'r') as file:
            self.board = file.readline().strip().split()
        
        self.size = int(len(self.board) ** 0.5)
        self.create_board()
    
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
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)
    
    def solve_puzzle(self):
        initial_state = PuzzleState(self.board)
        goal = [str(i) for i in range(1, self.size * self.size)] + ['X']
        self.log("🔍 Resolvendo com DFS...")
        
        solution, nodes, elapsed_time, memory_used = dfs(initial_state, goal, self.size, self.log)
        
        if solution:
            path = reconstruct_path(solution)
            for state in path:
                self.update_board(state.board)
            self.log(f"\n✅ Solução encontrada!")
            self.log(f"Nós visitados: {nodes}")
            self.log(f"Tempo de execução: {elapsed_time:.4f}s")
            self.log(f"Memória utilizada: {memory_used / 1024:.2f} KB")
        else:
            self.log("❌ Nenhuma solução encontrada.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()
