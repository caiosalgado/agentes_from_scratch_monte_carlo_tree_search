"""
Exemplo de uso do algoritmo Monte Carlo Tree Search com Self-Refine
"""

import aisuite as ai
from factory import create_mcts_algorithm


def main():
    """Exemplo básico de uso do algoritmo MCTSr"""
    
    # Configurar cliente LLM
    client = ai.Client()
    client.configure({
        "ollama": {
            "timeout": 600
        }
    })
    
    # Criar algoritmo MCTS
    mcts = create_mcts_algorithm(
        client=client, 
        model_name="ollama:qwen3:14b", 
        max_iterations=16
    )
    
    # Exemplo de problema matemático
    example = {
        "problem": "Find the number of positive integers n ≤ 100 such that n² + 1 is divisible by 3.",
        "answer": "33"
    }
    
    question = example['problem']
    ground_truth = example['answer']
    
    print(f"Pergunta: {question}")
    print(f"Resposta esperada: {ground_truth}")
    print("-" * 50)
    
    # Executar refinamento
    try:
        final_answer = mcts.run_mcts_refinement(question, ground_truth)
        print(f"Resposta final do algoritmo: {final_answer}")
        
        # Mostrar estatísticas da árvore
        mcts.print_tree_statistics()
        
    except Exception as e:
        print(f"Erro durante execução: {e}")


if __name__ == "__main__":
    main() 