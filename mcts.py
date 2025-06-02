import math
import time
from typing import List, Dict, Any, Optional, Tuple
from llm import LLM
from code_executor import CodeExecutor


class MCTSNode:
    """Nó da árvore MCTS"""
    def __init__(self, problem: Dict, code: str = "", parent: Optional['MCTSNode'] = None):
        self.problem = problem
        self.code = code
        self.parent = parent
        self.children: List['MCTSNode'] = []
        
        # Dados MCTS
        self.rewards: List[float] = []
        self.visit_count = 0
        self.ucb_value = 0.0
        
        # Dados específicos
        self.test_results: List[bool] = []
        self.test_outputs: List[str] = []
        self.hints = ""
        self.conversation_history: List[str] = []
        self.execution_time = 0.0
        self.is_solution = False
    
    def add_reward(self, reward: float):
        """Adiciona reward ao nó"""
        self.rewards.append(reward)
        self.visit_count += 1
    
    def get_average_reward(self) -> float:
        """Retorna reward médio"""
        return sum(self.rewards) / len(self.rewards) if self.rewards else 0.0
    
    def get_success_rate(self) -> float:
        """Retorna taxa de sucesso nos testes"""
        if not self.test_results:
            return 0.0
        return sum(self.test_results) / len(self.test_results)
    
    def is_fully_solved(self) -> bool:
        """Verifica se resolveu completamente"""
        return self.test_results and all(self.test_results)


class MCTS:
    def __init__(self, llm: LLM, code_executor: CodeExecutor, max_iter: int = 16, max_child: int = 3):
        self.llm = llm
        self.code_executor = code_executor
        self.max_iter = max_iter
        self.max_child = max_child
        self.exploration_constant = 1.4
        
        # Estado interno
        self._current_problem = None
        self._root = None
        self._debug_mode = False
        self._iteration_count = 0
        self._best_solution = None
        self._all_nodes: List[MCTSNode] = []
        self._execution_history = []
        self._start_time = 0.0
        self._total_time = 0.0
    
    def solve(self, problem: Dict) -> Optional[str]:
        """Executa MCTS completo para resolver problema"""
        print(f"🎯 Resolvendo: {problem.get('title', 'Problema desconhecido')}")
        
        self._setup_solve(problem)
        
        # Loop principal MCTS
        for iteration in range(self.max_iter):
            self._iteration_count = iteration + 1
            
            # Fase Selection
            selected_node = self._selection_phase()
            
            # Fase Expansion
            new_node = self._expansion_phase(selected_node)
            if not new_node:
                continue
            
            # Fase Simulation
            reward = self._simulation_phase(new_node)
            
            # Fase Backpropagation
            self._backpropagation_phase(new_node, reward)
            
            # Early stopping se encontrou solução
            if new_node.is_fully_solved():
                self._best_solution = new_node.code
                print(f"✅ Solução encontrada na iteração {iteration + 1}!")
                break
        
        self._total_time = time.time() - self._start_time
        
        # Retorna melhor solução encontrada
        if not self._best_solution:
            self._best_solution = self._get_best_solution()
        
        return self._best_solution
    
    def debug(self, problem: Dict):
        """Entra em modo debug para execução passo a passo"""
        print(f"🐛 Modo DEBUG ativado para: {problem.get('title', 'Problema')}")
        self._setup_solve(problem)
        self._debug_mode = True
        print("Use .step() para avançar uma iteração por vez")
    
    def step(self) -> bool:
        """Executa uma iteração MCTS (modo debug)"""
        if not self._debug_mode:
            raise Exception("Use .debug(problem) primeiro para ativar modo debug")
        
        if self._iteration_count >= self.max_iter:
            print("❌ Máximo de iterações atingido")
            return False
        
        print(f"\n=== ITERAÇÃO {self._iteration_count + 1} ===")
        
        # Executa uma iteração completa
        selected_node = self._selection_phase()
        print(f"🎯 SELEÇÃO: Node com {len(selected_node.code)} chars de código (UCB: {selected_node.ucb_value:.3f})")
        
        new_node = self._expansion_phase(selected_node)
        if not new_node:
            print("❌ Falha na expansão")
            return False
        
        print(f"📝 EXPANSÃO: Novo código gerado")
        print(f"   Código: {new_node.code[:100]}{'...' if len(new_node.code) > 100 else ''}")
        
        reward = self._simulation_phase(new_node)
        print(f"⚡ SIMULAÇÃO: {sum(new_node.test_results)}/{len(new_node.test_results)} testes passaram")
        print(f"   Reward: {reward:.2f}")
        
        self._backpropagation_phase(new_node, reward)
        print(f"🌳 BACKPROPAGATION: Árvore atualizada")
        
        self._iteration_count += 1
        
        if new_node.is_fully_solved():
            print("🎉 SOLUÇÃO COMPLETA ENCONTRADA!")
            self._best_solution = new_node.code
            return False
        
        print(f"📊 Próximo UCB mais alto: {max(n.ucb_value for n in self._all_nodes):.3f}")
        return True
    
    def metrics(self) -> Dict:
        """Retorna métricas da última execução"""
        if not self._current_problem:
            return {}
        
        best_node = self._get_best_node()
        
        return {
            'problem_id': self._current_problem.get('id', 'unknown'),
            'problem_title': self._current_problem.get('title', 'Unknown'),
            'solved': best_node.is_fully_solved() if best_node else False,
            'best_success_rate': best_node.get_success_rate() if best_node else 0.0,
            'iterations_used': self._iteration_count,
            'max_iterations': self.max_iter,
            'nodes_explored': len(self._all_nodes),
            'execution_time': self._total_time,
            'best_reward': best_node.get_average_reward() if best_node else 0.0,
            'total_llm_calls': len(self.llm.get_response_history())
        }
    
    def history(self) -> List[Dict]:
        """Retorna histórico completo de execução"""
        return self._execution_history.copy()
    
    def _setup_solve(self, problem: Dict):
        """Configura estado inicial para resolver problema"""
        self._current_problem = problem
        self._debug_mode = False
        self._iteration_count = 0
        self._best_solution = None
        self._all_nodes = []
        self._execution_history = []
        self._start_time = time.time()
        
        # Gera solução inicial
        initial_response, history = self.llm.generate_initial_solution(problem)
        initial_code = self.code_executor.extract_code(initial_response)
        
        # Cria nó raiz
        self._root = MCTSNode(problem, initial_code)
        self._root.conversation_history = history
        self._all_nodes.append(self._root)
        
        # Avalia solução inicial
        self._evaluate_node(self._root)
    
    def _selection_phase(self) -> MCTSNode:
        """Seleciona melhor nó usando UCB"""
        # Atualiza valores UCB
        self._update_ucb_values()
        
        # Filtra nós que ainda podem ser expandidos
        expandable_nodes = [n for n in self._all_nodes if len(n.children) < self.max_child]
        
        if not expandable_nodes:
            expandable_nodes = self._all_nodes
        
        # Seleciona nó com maior UCB
        best_node = max(expandable_nodes, key=lambda n: n.ucb_value)
        return best_node
    
    def _expansion_phase(self, selected_node: MCTSNode) -> Optional[MCTSNode]:
        """Expande nó selecionado gerando nova solução"""
        try:
            # Gera hints se código falhou
            hints = ""
            if selected_node.test_results and not all(selected_node.test_results):
                hints = self.llm.generate_hints(selected_node.problem, selected_node.code)
            
            # Gera solução melhorada
            improved_response, new_history = self.llm.generate_improved_solution(
                selected_node.problem, 
                hints, 
                selected_node.code, 
                selected_node.conversation_history
            )
            
            improved_code = self.code_executor.extract_code(improved_response)
            
            # Cria novo nó
            new_node = MCTSNode(selected_node.problem, improved_code, selected_node)
            new_node.hints = hints
            new_node.conversation_history = new_history
            
            # Adiciona como filho
            selected_node.children.append(new_node)
            self._all_nodes.append(new_node)
            
            return new_node
            
        except Exception as e:
            print(f"❌ Erro na expansão: {e}")
            return None
    
    def _simulation_phase(self, node: MCTSNode) -> float:
        """Avalia qualidade da solução do nó"""
        return self._evaluate_node(node)
    
    def _evaluate_node(self, node: MCTSNode) -> float:
        """Avalia nó executando código e calculando reward"""
        if not node.code.strip():
            node.add_reward(-100.0)
            return -100.0
        
        # Executa código
        start_time = time.time()
        results = self.code_executor.run_tests(node.code, node.problem['tests'])
        node.execution_time = time.time() - start_time
        
        # Atualiza estado do nó
        node.test_results = results['test_results']
        node.test_outputs = results['test_outputs']
        node.is_solution = results['success']
        
        # Calcula reward usando LLM
        llm_reward = self.llm.calculate_reward(
            node.problem, 
            node.code, 
            node.test_results, 
            node.test_outputs
        )
        
        # Combina reward do LLM com score de execução
        execution_score = results['score']
        combined_reward = (llm_reward + execution_score) / 2
        
        node.add_reward(combined_reward)
        
        # Salva no histórico
        self._execution_history.append({
            'iteration': self._iteration_count,
            'node_id': len(self._all_nodes) - 1,
            'code': node.code,
            'test_results': node.test_results,
            'reward': combined_reward,
            'execution_time': node.execution_time
        })
        
        return combined_reward
    
    def _backpropagation_phase(self, node: MCTSNode, reward: float):
        """Propaga reward pela árvore"""
        current = node.parent
        while current:
            current.add_reward(reward * 0.9)  # Decay para nós ancestrais
            current = current.parent
    
    def _update_ucb_values(self):
        """Atualiza valores UCB de todos os nós"""
        total_visits = sum(n.visit_count for n in self._all_nodes)
        
        for node in self._all_nodes:
            if node.visit_count == 0:
                node.ucb_value = float('inf')
            else:
                exploitation = node.get_average_reward()
                exploration = self.exploration_constant * math.sqrt(
                    math.log(total_visits + 1) / node.visit_count
                )
                node.ucb_value = exploitation + exploration
    
    def _get_best_solution(self) -> str:
        """Retorna melhor solução encontrada"""
        best_node = self._get_best_node()
        return best_node.code if best_node else ""
    
    def _get_best_node(self) -> Optional[MCTSNode]:
        """Retorna nó com melhor performance"""
        if not self._all_nodes:
            return None
        
        # Prioriza soluções completas
        complete_solutions = [n for n in self._all_nodes if n.is_fully_solved()]
        if complete_solutions:
            return max(complete_solutions, key=lambda n: n.get_average_reward())
        
        # Senão, retorna melhor parcial
        return max(self._all_nodes, key=lambda n: n.get_success_rate()) 