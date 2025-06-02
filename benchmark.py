import time
from typing import List, Dict, Any, Optional
from llm import LLM
from code_executor import CodeExecutor
from mcts import MCTS
from problems import Problems


def run_benchmark(problems: List[Dict], llm: LLM, code_executor: CodeExecutor, 
                  max_iter: int = 16, max_child: int = 3, 
                  verbose: bool = True) -> Dict:
    """
    Executa MCTS em todos os problemas e retorna métricas agregadas
    
    Args:
        problems: Lista de problemas para resolver
        llm: Instância do LLM
        code_executor: Instância do CodeExecutor  
        max_iter: Máximo de iterações MCTS
        max_child: Máximo de filhos por nó
        verbose: Se deve mostrar progresso
        
    Returns:
        Dict com resultados individuais e métricas agregadas
    """
    
    results = []
    total_problems = len(problems)
    solved_count = 0
    total_start_time = time.time()
    
    if verbose:
        print(f"🚀 Iniciando benchmark com {total_problems} problemas")
        print(f"⚙️ Configuração: max_iter={max_iter}, max_child={max_child}")
        print("-" * 60)
    
    for i, problem in enumerate(problems):
        if verbose:
            print(f"\n[{i+1}/{total_problems}] {problem.get('title', 'Problema desconhecido')}")
        
        try:
            # Cria nova instância MCTS para cada problema
            mcts = MCTS(llm, code_executor, max_iter=max_iter, max_child=max_child)
            
            # Resolve problema
            problem_start_time = time.time()
            solution = mcts.solve(problem)
            problem_time = time.time() - problem_start_time
            
            # Obtém métricas
            metrics = mcts.metrics()
            
            # Resultado individual
            result = {
                'problem_id': problem.get('id', f'problem_{i}'),
                'problem_title': problem.get('title', f'Problem {i+1}'),
                'solved': metrics.get('solved', False),
                'solution_code': solution or "",
                'test_success_rate': metrics.get('best_success_rate', 0.0),
                'iterations_used': metrics.get('iterations_used', 0),
                'nodes_explored': metrics.get('nodes_explored', 0),
                'execution_time': problem_time,
                'best_reward': metrics.get('best_reward', 0.0),
                'llm_calls': metrics.get('total_llm_calls', 0)
            }
            
            if result['solved']:
                solved_count += 1
                if verbose:
                    print(f"✅ Resolvido em {result['iterations_used']} iterações ({problem_time:.1f}s)")
            else:
                if verbose:
                    success_rate = result['test_success_rate']
                    print(f"❌ Não resolvido - {success_rate:.1%} dos testes passaram ({problem_time:.1f}s)")
            
            results.append(result)
            
        except Exception as e:
            if verbose:
                print(f"💥 Erro: {e}")
            
            results.append({
                'problem_id': problem.get('id', f'problem_{i}'),
                'problem_title': problem.get('title', f'Problem {i+1}'),
                'solved': False,
                'error': str(e),
                'execution_time': 0.0,
                'test_success_rate': 0.0,
                'iterations_used': 0,
                'nodes_explored': 0,
                'best_reward': -100.0,
                'llm_calls': 0
            })
    
    # Calcula métricas agregadas
    total_time = time.time() - total_start_time
    solved_results = [r for r in results if r.get('solved', False)]
    
    summary = {
        'total_problems': total_problems,
        'solved_problems': solved_count,
        'success_rate': solved_count / total_problems if total_problems > 0 else 0.0,
        'total_execution_time': total_time,
        'avg_time_per_problem': total_time / total_problems if total_problems > 0 else 0.0,
        'avg_iterations_for_solved': sum(r['iterations_used'] for r in solved_results) / len(solved_results) if solved_results else 0.0,
        'avg_nodes_for_solved': sum(r['nodes_explored'] for r in solved_results) / len(solved_results) if solved_results else 0.0,
        'avg_reward_for_solved': sum(r['best_reward'] for r in solved_results) / len(solved_results) if solved_results else 0.0,
        'total_llm_calls': sum(r.get('llm_calls', 0) for r in results),
        'avg_test_success_rate': sum(r.get('test_success_rate', 0) for r in results) / len(results) if results else 0.0
    }
    
    if verbose:
        print_benchmark_summary(summary)
    
    return {
        'individual_results': results,
        'summary': summary,
        'config': {
            'max_iter': max_iter,
            'max_child': max_child,
            'llm_model': llm.model_name
        }
    }


def print_benchmark_summary(summary: Dict):
    """Imprime resumo formatado do benchmark"""
    print("\n" + "="*60)
    print("📊 RESUMO DO BENCHMARK")
    print("="*60)
    print(f"✅ Problemas resolvidos: {summary['solved_problems']}/{summary['total_problems']} ({summary['success_rate']:.1%})")
    print(f"⏱️  Tempo total: {summary['total_execution_time']:.1f}s")
    print(f"⚡ Tempo médio por problema: {summary['avg_time_per_problem']:.1f}s")
    print(f"🔄 Iterações médias (resolvidos): {summary['avg_iterations_for_solved']:.1f}")
    print(f"🌳 Nós médios explorados (resolvidos): {summary['avg_nodes_for_solved']:.1f}")
    print(f"🎯 Reward médio (resolvidos): {summary['avg_reward_for_solved']:.1f}")
    print(f"🤖 Total de chamadas LLM: {summary['total_llm_calls']}")
    print(f"📈 Taxa média de sucesso em testes: {summary['avg_test_success_rate']:.1%}")


def save_benchmark_results(results: Dict, filename: str = "benchmark_results.json"):
    """Salva resultados do benchmark em arquivo JSON"""
    import json
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Resultados salvos em {filename}")
    except Exception as e:
        print(f"❌ Erro ao salvar resultados: {e}")


def run_single_problem_benchmark(problem_id: str, problems_file: str = "leetcode_problems.json",
                                max_iter: int = 16, max_child: int = 3) -> Dict:
    """Executa benchmark em um único problema específico"""
    
    # Carrega problemas
    problems = Problems()
    all_problems = problems.load_json(problems_file)
    
    # Encontra problema específico
    target_problem = None
    for p in all_problems:
        if p.get('id') == problem_id:
            target_problem = p
            break
    
    if not target_problem:
        raise ValueError(f"Problema '{problem_id}' não encontrado")
    
    # Configura componentes
    llm = LLM()
    code_executor = CodeExecutor()
    
    # Executa benchmark
    return run_benchmark([target_problem], llm, code_executor, max_iter, max_child) 