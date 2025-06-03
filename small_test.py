#%% Setup inicial - Importações e configuração
import json
from llm import LLM
from code_executor import CodeExecutor
from problems import Problems
from mcts import MCTS

print("Setup inicial completo!")

#%% Carregar problemas
problems = Problems()
problem_list = problems.load_json("leetcode_problems.json")
first_problem = problems[6]

print(f"Carregados {len(problem_list)} problemas")
print(f"Primeiro problema: {first_problem.get('title', 'Sem título')}")
print(f"ID: {first_problem.get('id', 'Sem ID')}")

#%% Inicializar componentes
llm = LLM()
code_executor = CodeExecutor()
mcts = MCTS(llm=llm, code_executor=code_executor, max_iter=5, max_child=2)

print("Componentes inicializados:")
print(f"- LLM configurado")
print(f"- Code Executor configurado") 
print(f"- MCTS configurado (max_iter=5, max_child=2)")

#%% Entrar em modo debug
mcts.debug(first_problem)

print("Modo debug ativado!")
print(f"Problema selecionado: {first_problem.get('title')}")

#%% Executar primeira iteração
can_continue = mcts.step()

print(f"Primeira iteração concluída")
print(f"Pode continuar: {can_continue}")

#%%
# Verificar métricas
metrics = mcts.metrics()
print(f"Iterações usadas: {metrics.get('iterations_used', 0)}")
print(f"Nós explorados: {metrics.get('nodes_explored', 0)}")
print(f"Resolvido: {metrics.get('solved', False)}")

#%%
#%% Funções de visualização da árvore
def print_tree_structure(mcts):
    """Mostra estrutura hierárquica da árvore"""
    print("🌳 ESTRUTURA DA ÁRVORE MCTS:")
    print("=" * 50)
    
    def print_node(node, level=0, node_id=None):
        indent = "  " * level
        if node_id is None:
            node_id = mcts._all_nodes.index(node) if node in mcts._all_nodes else "?"
        
        # Status do nó
        status = "✅ RESOLVIDO" if node.is_fully_solved() else "❌ PENDENTE"
        success_rate = node.get_success_rate()
        avg_reward = node.get_average_reward()
        
        print(f"{indent}📦 Nó {node_id} {status}")
        print(f"{indent}   Taxa sucesso: {success_rate:.2f}")
        print(f"{indent}   Reward médio: {avg_reward:.2f}")
        print(f"{indent}   Visitas: {node.visit_count}")
        print(f"{indent}   UCB: {node.ucb_value:.3f}")
        print(f"{indent}   Filhos: {len(node.children)}")
        print(f"{indent}   Código: {len(node.code)} chars")
        
        # Mostra filhos recursivamente
        for i, child in enumerate(node.children):
            child_id = mcts._all_nodes.index(child) if child in mcts._all_nodes else f"{node_id}.{i}"
            print_node(child, level + 1, child_id)
    
    if mcts._root:
        print_node(mcts._root, 0, 0)
    else:
        print("❌ Nenhuma árvore encontrada")

def print_node_details(mcts, node_id):
    """Mostra detalhes completos de um nó específico"""
    if node_id >= len(mcts._all_nodes):
        print(f"❌ Nó {node_id} não existe")
        return
    
    node = mcts._all_nodes[node_id]
    
    print(f"🔍 DETALHES DO NÓ {node_id}:")
    print("=" * 50)
    
    print(f"📊 MÉTRICAS:")
    print(f"   Visitas: {node.visit_count}")
    print(f"   Rewards: {node.rewards}")
    print(f"   Reward médio: {node.get_average_reward():.2f}")
    print(f"   Taxa sucesso: {node.get_success_rate():.2f}")
    print(f"   UCB: {node.ucb_value:.3f}")
    print(f"   É solução: {node.is_fully_solved()}")
    
    print(f"\n🧪 TESTES:")
    print(f"   Resultados: {node.test_results}")
    print(f"   Outputs: {node.test_outputs}")
    
    print(f"\n💡 HINTS:")
    print(f"   {node.hints[:200]}{'...' if len(node.hints) > 200 else ''}")
    
    print(f"\n👨‍👩‍👧‍👦 FAMÍLIA:")
    print(f"   Pai: {mcts._all_nodes.index(node.parent) if node.parent else 'Nenhum (raiz)'}")
    print(f"   Filhos: {[mcts._all_nodes.index(child) for child in node.children]}")
    
    print(f"\n💬 CONVERSAÇÃO ({len(node.conversation_history)} mensagens):")
    for i, msg in enumerate(node.conversation_history[-4:]):  # Últimas 4 mensagens
        role = "🤖 LLM" if i % 2 == 1 else "👤 USER" 
        print(f"   {role}: {msg[:100]}{'...' if len(msg) > 100 else ''}")
    
    print(f"\n💻 CÓDIGO ({len(node.code)} chars):")
    print("─" * 50)
    print(node.code)
    print("─" * 50)

def print_llm_history(mcts):
    """Mostra histórico completo de chamadas LLM"""
    history = mcts.llm.get_response_history()
    
    print(f"🤖 HISTÓRICO DO LLM ({len(history)} chamadas):")
    print("=" * 50)
    
    for i, call in enumerate(history):
        print(f"\n📞 CHAMADA {i+1}:")
        print(f"   Modelo: {call['model']}")
        print(f"   Prompt: {call['prompt'][:150]}{'...' if len(call['prompt']) > 150 else ''}")
        print(f"   Resposta: {call['response'][:150]}{'...' if len(call['response']) > 150 else ''}")

def print_execution_history(mcts):
    """Mostra histórico de execução das iterações"""
    history = mcts.history()
    
    print(f"⚡ HISTÓRICO DE EXECUÇÃO ({len(history)} registros):")
    print("=" * 50)
    
    for record in history:
        print(f"\n🔄 ITERAÇÃO {record['iteration']}:")
        print(f"   Nó: {record['node_id']}")
        print(f"   Testes: {sum(record['test_results'])}/{len(record['test_results'])}")
        print(f"   Reward: {record['reward']:.2f}")
        print(f"   Tempo: {record['execution_time']:.2f}s")
        print(f"   Código: {record['code'][:100]}{'...' if len(record['code']) > 100 else ''}")

print("Funções de visualização criadas!")

#%% Visualizar estrutura da árvore
print_tree_structure(mcts)

#%% Visualizar detalhes do nó raiz (0)
print_node_details(mcts, 0)

#%% Visualizar detalhes do nó filho (1)
print_node_details(mcts, 1)

#%% Visualizar histórico do LLM
print_llm_history(mcts)

#%% Visualizar histórico de execução
print_execution_history(mcts)

#%% Comparar códigos dos dois nós
print("🔄 COMPARAÇÃO DE CÓDIGOS:")
print("=" * 50)

print("📦 NÓ 0 (RAIZ - Solução inicial):")
print("─" * 30)
print(mcts._all_nodes[0].code)

print("\n📦 NÓ 1 (FILHO - Solução melhorada):")
print("─" * 30)
print(mcts._all_nodes[1].code)

print(f"\nDiferenças:")
print(f"  Nó 0: {len(mcts._all_nodes[0].code)} chars, {mcts._all_nodes[0].get_success_rate():.2f} sucesso")
print(f"  Nó 1: {len(mcts._all_nodes[1].code)} chars, {mcts._all_nodes[1].get_success_rate():.2f} sucesso")

#%%
#%% Verificar execução atual
node = mcts._all_nodes[1]
problem = node.problem
code_executor = mcts.code_executor

# Testar execução atual
result = code_executor.run_tests(node.code, problem)
print("Resultado atual:", result)

#%% Ver código extraído vs original
print("Código do nó:")
print(repr(node.code))
print("\nFunção detectada:")
print(code_executor.function_pattern.findall(node.code))

#%% Testar um caso manualmente
test_case = problem['tests'][0] 
print("Teste:", test_case)

# Executar diretamente
namespace = {}
exec(node.code, namespace)
func_name = list(namespace.keys())[-1]  # última função definida
func = namespace[func_name]

# Chamar função
inputs = test_case['input']
if len(inputs) == 1:
    result = func(inputs[0])
else:
    result = func(*inputs)

print(f"Input: {inputs}")
print(f"Expected: {test_case['expected']}")  
print(f"Got: {result}")
print(f"Match: {result == test_case['expected']}")
print(f"Types: got={type(result)}, expected={type(test_case['expected'])}")

#%% Executar segunda iteração
if can_continue:
    can_continue = mcts.step()
    
    print(f"Segunda iteração concluída")
    print(f"Pode continuar: {can_continue}")
    
    # Métricas atualizadas
    metrics = mcts.metrics()
    print(f"Iterações usadas: {metrics.get('iterations_used', 0)}")
    print(f"Taxa de sucesso atual: {metrics.get('best_success_rate', 0.0):.2f}")

#%% Executar terceira iteração
if can_continue:
    can_continue = mcts.step()
    
    print(f"Terceira iteração concluída")
    print(f"Pode continuar: {can_continue}")
    
    metrics = mcts.metrics()
    print(f"Iterações usadas: {metrics.get('iterations_used', 0)}")
    print(f"Reward médio: {metrics.get('best_reward', 0.0):.2f}")

#%% Executar iterações restantes
while can_continue:
    can_continue = mcts.step()
    if not can_continue:
        break

print("Todas as iterações concluídas!")

# Métricas finais
metrics = mcts.metrics()
print("\nMétricas finais:")
for key, value in metrics.items():
    print(f"  {key}: {value}")

#%% Verificar melhor solução encontrada
best_solution = mcts._get_best_solution()

print("Melhor solução encontrada:")
print("="*50)
print(best_solution)
print("="*50)

#%% Testar execução normal (sem debug)
print("Testando execução normal (não-debug)...")

mcts_normal = MCTS(llm=llm, code_executor=code_executor, max_iter=8, max_child=3)
solution = mcts_normal.solve(first_problem)

print("Execução normal concluída!")
metrics_normal = mcts_normal.metrics()
print(f"Resolvido: {metrics_normal.get('solved', False)}")
print(f"Iterações usadas: {metrics_normal.get('iterations_used', 0)}")
print(f"Tempo de execução: {metrics_normal.get('execution_time', 0.0):.2f}s")

#%% Comparar resultados
print("\nComparação debug vs normal:")
print(f"Debug - Resolvido: {metrics.get('solved', False)} | Iterações: {metrics.get('iterations_used', 0)}")
print(f"Normal - Resolvido: {metrics_normal.get('solved', False)} | Iterações: {metrics_normal.get('iterations_used', 0)}")

if solution:
    print(f"Solução normal tem {len(solution)} caracteres")
if best_solution:
    print(f"Solução debug tem {len(best_solution)} caracteres")