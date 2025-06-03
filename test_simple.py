#!/usr/bin/env python3
"""Script simples para testar todos os problemas do LeetCode"""

import time
import json
from llm import LLM
from code_executor import CodeExecutor
from problems import Problems
from mcts import MCTS


def test_all_problems():
    """Testa todos os problemas e mostra resultados simples"""
    
    # Setup
    llm = LLM()
    code_executor = CodeExecutor()
    problems = Problems()
    all_problems = problems.load_json("leetcode_problems.json")
    
    print(f"🚀 Testando {len(all_problems)} problemas...")
    print("-" * 60)
    
    results = []
    solved_count = 0
    
    for i, problem in enumerate(all_problems, 1):
        title = problem.get('title', f'Problem {i}')
        problem_id = problem.get('id', f'problem_{i}')
        
        print(f"[{i}/{len(all_problems)}] {title}")
        
        # Cria MCTS e resolve
        mcts = MCTS(llm, code_executor, max_iter=16, max_child=3)
        
        start_time = time.time()
        solution = mcts.solve(problem)
        execution_time = time.time() - start_time
        
        # Pega métricas
        metrics = mcts.metrics()
        solved = metrics.get('solved', False)
        iterations = metrics.get('iterations_used', 0)
        success_rate = metrics.get('best_success_rate', 0.0)
        
        # Resultado
        result = {
            'id': problem_id,
            'title': title,
            'solved': solved,
            'iterations': iterations,
            'time': execution_time,
            'success_rate': success_rate
        }
        
        results.append(result)
        
        if solved:
            solved_count += 1
            print(f"  ✅ Resolvido em {iterations} iterações - Tempo: {execution_time:.1f}s")
        else:
            tests_passed = int(success_rate * len(problem.get('tests', [])))
            total_tests = len(problem.get('tests', []))
            print(f"  ❌ {tests_passed}/{total_tests} testes - Tempo: {execution_time:.1f}s")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    print(f"Resolvidos: {solved_count}/{len(all_problems)} ({solved_count/len(all_problems):.1%})")
    
    # Estatísticas dos resolvidos
    solved_results = [r for r in results if r['solved']]
    if solved_results:
        avg_iterations = sum(r['iterations'] for r in solved_results) / len(solved_results)
        avg_time = sum(r['time'] for r in solved_results) / len(solved_results)
        print(f"Média (resolvidos): {avg_iterations:.1f} iterações, {avg_time:.1f}s")
    
    # Salva resultados
    with open('resultados_simples.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Resultados salvos em: resultados_simples.json")
    
    return results


if __name__ == "__main__":
    test_all_problems() 