# Monte Carlo Tree Search com Self-Refine

Este projeto implementa um algoritmo Monte Carlo Tree Search (MCTS) com capacidades de auto-refinamento para melhoria iterativa de respostas geradas por LLMs.

## Estrutura do Projeto

```
├── mcts_node.py          # Classe MCTSNode - representa nós da árvore
├── llm_interface.py      # Classe LLMInterface - interface para LLMs
├── answer_validator.py   # Classe AnswerValidator - validação de respostas
├── mcts_algorithm.py     # Classe principal MCTSRefinementAlgorithm
├── factory.py           # Factory function para criar instâncias
├── __init__.py          # Configuração do pacote
└── README.md           # Esta documentação
```

## Como Funciona

O algoritmo MCTSr implementa uma busca em árvore Monte Carlo para refinamento iterativo de respostas matemáticas usando LLMs:

1. **Inicialização**: Cria estruturas de dados para gerenciar nós da árvore
2. **Resposta Inicial**: Gera uma resposta inicial fraca e uma baseline negativa
3. **Iterações de Refinamento**: Executa até n iterações onde:
   - Usa UCB (Upper Confidence Bound) para selecionar o melhor nó
   - Gera hints críticos sobre a resposta selecionada
   - Cria resposta melhorada baseada nos hints
   - Avalia respostas usando LLM crítico (scores -100 a +100)
   - Atualiza valores UCB para guiar futuras seleções
4. **Early Stopping**: Para quando encontra resposta correta
5. **Histórico**: Mantém histórico completo de conversação para cada nó

## Componentes Principais

### MCTSNode
Representa um nó na árvore de busca com:
- Query original
- Lista de rewards
- Hints gerados
- Resposta predita e real
- Histórico de conversação
- Estrutura de árvore (pai/filhos)

### LLMInterface
Encapsula todas as interações com LLM:
- Geração de respostas fracas
- Geração de hints
- Criação de respostas melhoradas
- Cálculo de scores de reward
- Prompts de refinamento

### AnswerValidator
Valida e extrai respostas:
- Extração de labels numéricos
- Verificação de correção
- Determinação de formato de resposta

### MCTSRefinementAlgorithm
Algoritmo principal que coordena:
- Fases MCTS (seleção, expansão, simulação, backpropagation)
- Cálculos UCB
- Gerenciamento da árvore
- Cache de rewards e hints

## Uso Básico

```python
import aisuite as ai
from factory import create_mcts_algorithm

# Configurar cliente LLM
client = ai.Client()
client.configure({
    "ollama": {"timeout": 600}
})

# Criar algoritmo MCTS
mcts = create_mcts_algorithm(client, max_iterations=16)

# Executar refinamento
question = "Find the number of positive integers n ≤ 100 such that n² + 1 is divisible by 3."
ground_truth = "33"

final_answer = mcts.run_mcts_refinement(question, ground_truth)
print(f"Resposta final: {final_answer}")
```

## Status de Implementação

Atualmente todas as classes estão criadas com métodos definidos usando `pass`. A implementação será feita incrementalmente, método por método.

## Próximos Passos

1. Implementar métodos básicos do MCTSNode
2. Implementar interface LLM
3. Implementar validador de respostas
4. Implementar algoritmo principal MCTS
5. Testes e refinamentos 