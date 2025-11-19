# Maze Runner — Pathfinding with A* and BFS

This project implements two fundamental pathfinding algorithms — **A*** and **Breadth-First Search (BFS)** — to solve dynamic maze-navigation problems in Python. It provides a modular framework for experimenting with heuristics, analyzing algorithmic behavior, and benchmarking performance across various maze structures.

## 🚀 Features

- **A*** algorithm with priority queues and Manhattan-distance heuristic  
- **BFS** for guaranteed shortest-path search in unweighted mazes  
- **Dynamic maze generation** and customizable grids  
- **Time–space complexity analysis** across runs  
- **Memory-efficient data structures** for optimized performance  
- **Clean, modular Python implementation**

## 📂 Project Structure

```
├── astar.py          # A* implementation
├── mazerunner.py     # Maze logic + BFS + runner script
└── README.md         # Documentation
```

## 🧠 Algorithms

### Breadth-First Search (BFS)
- Explores nodes level by level  
- Guarantees shortest path  
- Simple but may use more memory on large grids  

### A* Search
- f(n) = g(n) + h(n)  
- Combines path cost + heuristic (Manhattan)  
- Efficient for complex or large mazes  
- Uses a priority queue for expansion ordering  

## 🛠️ Installation & Usage

### Clone the repository
```bash
git clone https://github.com/yourusername/maze-runner.git
cd maze-runner
```

### Run Maze Runner
```bash
python mazerunner.py
```

### Run A*
```bash
python astar.py
```

## 📊 Example Output

- Path coordinates  
- Nodes explored  
- Runtime comparisons  
- Optional scalability benchmarks  

## 📈 Future Enhancements

- Add visualization (Pygame / Matplotlib)  
- Support weighted grids  
- Add Dijkstra, Greedy-Best-First, IDA*  
- Improve benchmarking suite  

## 🤝 Contributing

Pull requests and suggestions are welcome!
