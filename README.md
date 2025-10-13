# 🧠 AI Problem Solving Repository

Welcome to the **AI_Problem_Solving** repository — a comprehensive collection of artificial intelligence implementations designed to explore core concepts in **search algorithms**, **constraint satisfaction problems**, and **adversarial reasoning**.  
Each module focuses on a classical AI domain problem, combining theory with practical, visual, and algorithmic implementations.

---

## 📁 Repository Structure

| Module | Description |
|:--|:--|
| **1️⃣ Smart City Grid** | Simulation of a dynamic grid environment representing a smart city with autonomous agents using heuristic search for optimal pathfinding and traffic management. |
| **2️⃣ Mars Rover Problem** | Implementation of rover navigation across a terrain grid using BFS, DFS, UCS, and A* algorithms to determine optimal exploration routes under varying cost conditions. |
| **3️⃣ Pacman Problem** | Classic AI search problem featuring Pacman’s intelligent movement through a maze using uninformed and informed search strategies with path visualization. |
| **4️⃣ Adversarial Search using Checkers** | Implementation of adversarial search for the game of Checkers using **Minimax** and **Alpha–Beta pruning**, demonstrating optimal decision-making under competitive settings. |
| **5️⃣ Constraint Satisfaction Problems (CSP)** | CSP solutions for **Sudoku** and **University Timetable Scheduling** problems using **Backtracking**, **AC-3 consistency**, and **MRV heuristics** for efficient constraint propagation. |
| **6️⃣ Search Algorithms** | Foundational AI search algorithms implemented from scratch — **BFS**, **DFS**, **UCS**, and **A\*** — with visual representations and comparative performance metrics. |

---

## ⚙️ Tech Stack

- **Language:** Python 3.10+
- **Libraries Used:**  
  - `numpy`, `pandas` – data handling  
  - `pygame`, `streamlit`, `matplotlib` – visualization & UI  
  - `heapq`, `queue`, `collections` – core data structures  
  - `time`, `copy`, `random` – simulation and control  

---

## 🧩 Module Overviews

### 🏙️ Smart City Grid
A grid-based AI simulation representing a smart city traffic network.  
Agents navigate roads using heuristic-driven pathfinding (A\*, UCS) while dynamically adapting to congestion and road closures.  
Supports visual visualization in **Streamlit** or **Pygame**.

**Features:**
- Dynamic obstacle generation (roadblocks, traffic)
- Shortest path detection using multiple algorithms
- Real-time visualization

---

### 🚀 Mars Rover Problem
Inspired by NASA’s exploration problem — simulate a rover navigating a terrain grid with different elevation or energy costs.  

**Highlights:**
- Multiple cost-based pathfinding algorithms (BFS, DFS, UCS, A\*)
- Terrain-based cost weighting
- Visual trace of rover’s optimal route

---

### 👻 Pacman Problem
A visualized Pacman agent navigating a maze environment while searching for food pellets using AI search algorithms.  

**Algorithms Implemented:**
- BFS (Breadth-First Search)
- DFS (Depth-First Search)
- UCS (Uniform Cost Search)
- A\* (A-star with Manhattan heuristic)

**Visualization:**  
Implemented using **Streamlit**, showing Pacman’s path exploration and solution trace.

---

### ♟️ Adversarial Search using Checkers
Implements a competitive two-player game agent using **Minimax** and **Alpha–Beta pruning**.  
Pacman’s environment is replaced by a **Checkers board** where the AI predicts opponent moves and optimizes decisions.

**Key Components:**
- State-space search
- Evaluation function for heuristic scoring
- Move generation, captures, and pruning
- Pygame visualization

---

### 🧮 Constraint Satisfaction Problems (CSP)
#### 🧩 Sudoku Solver
Solves Sudoku grids using:
- **Backtracking Search**
- **AC-3 (Arc Consistency)**
- **MRV (Minimum Remaining Values)** heuristic

#### 🏫 Timetable Scheduling
Generates conflict-free university timetables using:
- **Constraint satisfaction formulation**
- **Backtracking with domain pruning**
- **Hard constraint validation**

---

### 🔍 Search Algorithms
Core implementation of AI search strategies applicable to multiple domains (Pacman, Mars Rover, Smart City Grid).

| Algorithm | Type | Characteristics |
|------------|------|----------------|
| **BFS** | Uninformed | Explores level-wise, guarantees shortest path in uniform cost |
| **DFS** | Uninformed | Explores depth-first, may find suboptimal paths |
| **UCS** | Informed | Expands least-cost nodes first |
| **A\*** | Informed | Combines path cost + heuristic for optimality |

Includes:
- Step-by-step path reconstruction  
- Node expansion visualization  
- Cost analysis comparison charts

---

## 📊 Visual Demonstrations
Each module supports **interactive or graphical visualization** via:
- **Pygame** for real-time game/agent simulation  
- **Streamlit** for clean web-based demonstrations of search traces and CSP solving  

---

## 🧠 Learning Objectives

Through this repository, learners can:
- Understand **AI problem-solving paradigms** via practical coding.  
- Explore **heuristic search** and **state-space reasoning**.  
- Apply **constraint propagation** and **adversarial game theory**.  
- Visualize and analyze algorithmic behavior.

---
