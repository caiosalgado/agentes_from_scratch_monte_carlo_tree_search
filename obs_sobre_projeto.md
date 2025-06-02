# Descrição Completa do Projeto: Monte Carlo Tree Search para Resolução de Problemas de Programação

## **Visão Geral do Projeto**

Este projeto implementa um algoritmo **Monte Carlo Tree Search (MCTS) com Self-Refine** para resolver problemas de programação do LeetCode de forma iterativa usando Large Language Models (LLMs). O objetivo é criar um sistema que melhore progressivamente suas soluções através de refinamento baseado em feedback, medindo a taxa de sucesso em um conjunto de problemas padronizados.

## **Problema que Resolve**

LLMs frequentemente geram soluções de código que não funcionam na primeira tentativa. Este projeto usa MCTS para:
- Gerar múltiplas tentativas de solução
- Refinar soluções baseado em feedback de testes
- Explorar diferentes abordagens de forma inteligente
- Melhorar iterativamente até encontrar soluções corretas

## **Funcionamento do Algoritmo**

### **Fase 1: Inicialização**
1. Carrega problema do arquivo `leetcode_problems.json`
2. Gera solução inicial "fraca" usando LLM
3. Cria nó raiz da árvore MCTS
4. Executa testes e calcula reward inicial

### **Fase 2: Iterações MCTS (até 16 iterações)**
Para cada iteração:

**Selection**: Usa Upper Confidence Bound (UCB) para selecionar o nó mais promissor para explorar

**Expansion**: Gera nova solução refinada baseada em:
- Código atual do nó selecionado
- Hints sobre erros/melhorias
- Histórico de tentativas anteriores

**Simulation**: Executa o novo código contra os casos de teste e calcula reward baseado em:
- Quantos testes passaram
- Se há erros de sintaxe
- Qualidade da solução

**Backpropagation**: Propaga o reward pela árvore, atualizando valores UCB dos nós ancestrais

### **Fase 3: Finalização**
- Para quando encontra solução 100% correta (early stopping)
- Ou quando atinge máximo de iterações
- Retorna melhor solução encontrada

## **Estrutura dos Dados de Entrada**

O arquivo `leetcode_problems.json` contém problemas com estrutura:

```json
{
  "problems": [
    {
      "id": "twoSum",
      "title": "Two Sum", 
      "description": "Given an array of integers nums and an integer target...",
      "function_signature": "def twoSum(nums: List[int], target: int) -> List[int]:",
      "initial_code": "def twoSum(nums: List[int], target: int) -> List[int]:\n    # Your solution here\n    pass",
      "tests": [
        {"input": [[2, 7, 11, 15], 9], "expected": [0, 1]},
        {"input": [[3, 2, 4], 6], "expected": [1, 2]}
      ],
      "constraints": "2 <= nums.length <= 10^4..."
    }
  ]
}
```

## **Componentes Técnicos Necessários**

### **1. Estrutura de Dados da Árvore**
- **Nós MCTS**: Armazenam código, rewards, histórico, relações pai/filho
- **Valores UCB**: Para seleção inteligente de nós
- **Cache de resultados**: Para evitar re-execução desnecessária

### **2. Interface com LLM**
- **Geração de código inicial**: Prompt para solução básica
- **Refinamento**: Prompt com hints sobre erros/melhorias
- **Geração de hints**: Análise crítica de código que falha

### **3. Execução e Validação de Código**
- **Parser de código**: Extrai código Python das respostas do LLM
- **Execução segura**: Roda código em ambiente controlado
- **Validação de testes**: Compara outputs com expected results
- **Cálculo de rewards**: Score baseado em taxa de sucesso dos testes

### **4. Sistema de Benchmark**
- **Carregamento de problemas**: Parse do JSON
- **Execução em lote**: Roda MCTS em múltiplos problemas
- **Métricas**: Taxa de sucesso geral, tempo por problema, etc.
- **Relatórios**: Resultados detalhados e estatísticas

## **Parâmetros Configuráveis**

- **max_iterations**: Máximo de iterações MCTS (padrão: 16)
- **max_children_per_node**: Máximo de filhos por nó (padrão: 3)
- **exploration_constant**: Constante C do UCB (padrão: 1.4)
- **model_name**: Modelo LLM a usar (padrão: "ollama:qwen3:14b")
- **timeout**: Timeout para execução de código (padrão: 5s)

## **Métricas de Avaliação**

### **Por Problema**
- Solução encontrada (True/False)
- Número de iterações necessárias
- Tempo total de execução
- Número de nós explorados na árvore

### **Geral**
- Taxa de sucesso geral (% de problemas resolvidos)
- Tempo médio por problema
- Eficiência do algoritmo (soluções/iteração)
- Distribuição de dificuldade dos problemas resolvidos

## **Desafios Técnicos**

1. **Execução segura de código**: Evitar código malicioso ou loops infinitos
2. **Parsing de respostas LLM**: Extrair código válido de texto livre
3. **Cálculo de rewards**: Balancear diferentes tipos de erro/sucesso
4. **Eficiência**: Evitar re-execução desnecessária de código
5. **Prompts efetivos**: Gerar hints úteis para refinamento

## **Objetivo Final**

Demonstrar que MCTS pode melhorar significativamente a taxa de sucesso de LLMs em problemas de programação, comparado com tentativa única, através de refinamento iterativo inteligente.

