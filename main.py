#!/usr/bin/env python3
"""
Script principal para usar o sistema MCTS 
Demonstra a interface proposta pelo usuário
"""

from llm import LLM
from code_executor import CodeExecutor
from problems import Problems
from mcts import MCTS
from benchmark import run_benchmark, save_benchmark_results


def example_single_problem():
    """Exemplo de uso em um único problema"""
    print("🎯 EXEMPLO: RESOLVENDO UM PROBLEMA")
    print("="*50)
    
    # Setup conforme interface proposta
    llm = LLM()  # Implementa o ai.Client etc lá dentro
    code_executor = CodeExecutor()  # implementar uma forma segura de extrair o código e executar ele usando boas práticas
    problems = Problems().load_json("leetcode_problems.json")  # para carregar o json
    mcts = MCTS(llm=llm, code_executor=code_executor, max_iter=16, max_child=3)
    
    # Resolve primeiro problema
    solution = mcts.solve(problems[0])
    
    print("\n📊 MÉTRICAS:")
    metrics = mcts.metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\n📜 HISTÓRICO:")
    history = mcts.history()
    print(f"  Total de iterações registradas: {len(history)}")
    if history:
        print(f"  Primeira iteração: reward={history[0].get('reward', 'N/A')}")
        print(f"  Última iteração: reward={history[-1].get('reward', 'N/A')}")
    
    return solution


def example_debug_mode():
    """Exemplo do modo debug step-by-step"""
    print("\n🐛 EXEMPLO: MODO DEBUG")
    print("="*50)
    
    llm = LLM()
    code_executor = CodeExecutor()
    problems = Problems().load_json("leetcode_problems.json")
    mcts = MCTS(llm=llm, code_executor=code_executor, max_iter=16, max_child=3)
    
    # Entra em modo debug
    mcts.debug(problems[0])
    
    # Executa alguns steps manualmente
    print("\n🔄 Executando steps manuais:")
    for i in range(3):  # Apenas 3 steps para demonstração
        print(f"\n--- Step {i+1} ---")
        can_continue = mcts.step()
        if not can_continue:
            print("🏁 Execução terminou (solução encontrada ou limite atingido)")
            break
    
    print(f"\n📊 Métricas atuais:")
    metrics = mcts.metrics()
    print(f"  Resolvido: {metrics.get('solved', False)}")
    print(f"  Iterações usadas: {metrics.get('iterations_used', 0)}")
    print(f"  Nós explorados: {metrics.get('nodes_explored', 0)}")


def example_benchmark():
    """Exemplo de benchmark completo"""
    print("\n📊 EXEMPLO: BENCHMARK COMPLETO")
    print("="*50)
    
    llm = LLM()
    code_executor = CodeExecutor()
    problems = Problems().load_json("leetcode_problems.json")
    
    # Executa benchmark em primeiros 3 problemas (para exemplo)
    test_problems = problems[:3]
    
    results = run_benchmark(
        problems=test_problems,
        llm=llm,
        code_executor=code_executor,
        max_iter=16,
        max_child=3,
        verbose=True
    )
    
    # Salva resultados
    save_benchmark_results(results, "example_benchmark_results.json")
    
    return results


def example_prompt_customization():
    """Exemplo de customização de prompts"""
    print("\n✏️ EXEMPLO: CUSTOMIZAÇÃO DE PROMPTS")
    print("="*50)
    
    llm = LLM()
    
    # Mostra prompt original
    original = llm.prompts.show_prompt('get_weak_answer')
    print(f"Prompt original: {len(original)} chars")
    
    # Customiza prompts
    llm.prompts.add_before('get_weak_answer', "You are an expert Python programmer. ")
    llm.prompts.add_after('get_weak_answer', "\nFocus on clean, efficient code.")
    
    # Mostra prompt modificado
    modified = llm.prompts.show_prompt('get_weak_answer')
    print(f"Prompt modificado: {len(modified)} chars")
    
    # Substitui completamente um prompt
    llm.prompts.replace('call_reward', """
    Rate this Python solution on a scale from -100 to +100:
    
    Problem: {question}
    Code: {code}
    Test Results: {test_results}
    
    Consider correctness, efficiency, and code quality.
    Respond with just: Score: [number]
    """)
    
    print("✅ Prompts customizados com sucesso!")
    
    # Pode usar o LLM customizado normalmente
    code_executor = CodeExecutor()
    problems = Problems().load_json("leetcode_problems.json")
    mcts = MCTS(llm=llm, code_executor=code_executor, max_iter=5, max_child=2)
    
    print("🎯 Testando com prompts customizados...")
    solution = mcts.solve(problems[0])
    print(f"✅ Solução gerada com prompts customizados!")


def main():
    """Função principal demonstrando todos os usos"""
    print("🚀 SISTEMA MCTS - DEMONSTRAÇÃO DE USO")
    print("="*60)
    
    examples = [
        ("Problema único", example_single_problem),
        ("Modo debug", example_debug_mode),
        ("Benchmark", example_benchmark),
        ("Customização de prompts", example_prompt_customization)
    ]
    
    for example_name, example_func in examples:
        print(f"\n{'='*20} {example_name.upper()} {'='*20}")
        try:
            result = example_func()
            print(f"✅ {example_name} executado com sucesso!")
        except Exception as e:
            print(f"❌ Erro em {example_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("🎉 DEMONSTRAÇÃO COMPLETA!")
    print("💡 Agora você pode usar o sistema conforme mostrado nos exemplos.")


if __name__ == "__main__":
    main() 