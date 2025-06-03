# MCTS LeetCode Solver

A Python implementation of **Monte Carlo Tree Search (MCTS)** algorithm for automatically solving LeetCode programming problems using Large Language Models (LLMs).

## 🎯 Overview

This project combines the power of Monte Carlo Tree Search with LLMs to iteratively improve code solutions for algorithmic problems. The system explores different solution approaches, learns from test feedback, and converges on optimal solutions through guided search.

## 🏗️ Architecture

The system consists of four main components:

### Core Components

- **`MCTS`** - Main Monte Carlo Tree Search engine
- **`LLM`** - Language model interface for code generation and evaluation
- **`CodeExecutor`** - Safe code execution and testing environment
- **`Problems`** - Problem loader and management system

### Key Features

- **Iterative Improvement**: Uses MCTS to explore solution space systematically
- **Smart Exploration**: Balances exploitation of good solutions with exploration of new approaches
- **Automatic Stopping**: Terminates when optimal solution is found
- **Detailed Metrics**: Tracks iterations, execution time, and success rates
- **Comprehensive Testing**: Validates solutions against all test cases

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
uv add aisuite
```

### Basic Usage

```python
from llm import LLM
from code_executor import CodeExecutor
from problems import Problems
from mcts import MCTS

# Setup components
llm = LLM()
code_executor = CodeExecutor()
problems = Problems().load_json("leetcode_problems.json")

# Create MCTS solver
mcts = MCTS(llm=llm, code_executor=code_executor, max_iter=16, max_child=3)

# Solve a problem
solution = mcts.solve(problems[0])

# Get metrics
metrics = mcts.metrics()
print(f"Solved: {metrics['solved']}")
print(f"Iterations: {metrics['iterations_used']}")
print(f"Time: {metrics['execution_time']:.2f}s")
```

### Run All Tests

```bash
python test_simple.py
```

## 📊 Usage Examples

### Single Problem Solving

```python
# Solve one problem with custom configuration
mcts = MCTS(llm, code_executor, max_iter=20, max_child=4)
solution = mcts.solve(problem)
```

### Debug Mode (Step-by-step)

```python
# Enter debug mode for detailed analysis
mcts.debug(problem)

# Execute steps manually
while mcts.step():
    metrics = mcts.metrics()
    print(f"Iteration {metrics['iterations_used']}: {metrics['best_success_rate']:.1%}")
```

### Benchmark Multiple Problems

```python
from benchmark import run_benchmark

results = run_benchmark(
    problems=problems[:10],  # First 10 problems
    llm=llm,
    code_executor=code_executor,
    max_iter=16,
    max_child=3
)
```

## 🔧 Configuration

### MCTS Parameters

- **`max_iter`**: Maximum number of iterations (default: 16)
- **`max_child`**: Maximum children per node (default: 3)
- **`exploration_constant`**: UCB exploration parameter (default: 1.414)

## 📈 Algorithm Details

### MCTS Phases

1. **Selection**: Choose best node using UCB (Upper Confidence Bound)
2. **Expansion**: Generate improved solution using LLM
3. **Simulation**: Test solution against all test cases
4. **Backpropagation**: Update node values throughout tree

### Reward System

The system combines:
- **Test Success Rate**: Percentage of test cases passed
- **LLM Evaluation**: Quality assessment of code structure and efficiency
- **Execution Performance**: Runtime and memory efficiency

### Early Termination

The algorithm stops when:
- A complete solution is found (100% test cases pass)
- Maximum iterations reached
- No improvement for several iterations

## 📋 Output Format

### Individual Problem Results

```
[1/144] Two Sum
  ✅ Resolvido em 8 iterações - Tempo: 45.2s

[2/144] Add Two Numbers  
  ❌ 3/4 testes - Tempo: 67.1s
```

### Summary Statistics

```
📊 RESUMO FINAL
==============
Resolvidos: 89/144 (61.8%)
Média (resolvidos): 9.2 iterações, 52.3s
```

### JSON Results

Results are saved to `resultados_simples.json`:

```json
{
  "id": "two-sum",
  "title": "Two Sum",
  "solved": true,
  "iterations": 8,
  "time": 45.2,
  "success_rate": 1.0
}
```

## 🗂️ Project Structure

```
├── mcts.py              # Main MCTS algorithm
├── llm.py               # LLM interface and prompts
├── code_executor.py     # Code execution engine
├── problems.py          # Problem management
├── benchmark.py         # Benchmarking utilities
├── test_simple.py       # Simple test runner
├── main.py              # Usage examples
└── leetcode_problems.json # Problem dataset
```

## 🛡️ Safety Features

- **Sandboxed Execution**: Code runs in isolated environment
- **Timeout Protection**: Prevents infinite loops
- **Memory Limits**: Protects against memory exhaustion
- **Import Restrictions**: Only allows safe standard library modules

## 🎛️ Advanced Features

### Custom Prompts

```python
# Customize LLM prompts
llm.prompts.add_before('get_weak_answer', "You are an expert Python programmer.")
llm.prompts.replace('call_reward', "Rate this solution from -100 to +100...")
```

### Performance Monitoring

```python
# Get detailed execution history
history = mcts.history()
for record in history:
    print(f"Iteration {record['iteration']}: {record['reward']:.2f}")
```

## 📊 Performance Metrics

The system tracks comprehensive metrics:

- **Success Rate**: Percentage of problems completely solved
- **Average Iterations**: Mean iterations needed for successful solutions
- **Execution Time**: Time per problem and total runtime
- **Tree Statistics**: Nodes explored, tree depth, branching factor
- **LLM Usage**: Total API calls and token consumption

