import aisuite as ai
import re
from typing import List, Dict, Any, Tuple, Optional
from prompt_manager import PromptManager


class LLM:
    def __init__(self, model_name: str = "ollama:qwen3:14b"):
        self.model_name = model_name
        self.client = self._setup_client()
        self.prompts = PromptManager()
        self.timeout = 150
        self._response_history = []
    
    def _setup_client(self):
        """Configura cliente aisuite"""
        client = ai.Client()
        client.configure({
            "ollama": {
                "timeout": 600
            }
        })
        return client
    
    def _call_llm(self, prompt: str, history: Optional[List[str]] = None, truncate: bool = True) -> Tuple[str, List[str]]:
        """Chama o LLM com prompt e retorna resposta + histórico atualizado"""
        if history is None:
            history = []
        
        # Formata histórico de mensagens
        messages = []
        for i, h in enumerate(history):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": h})
        
        # Trunca histórico se necessário (mantém apenas as 2 últimas interações)
        if truncate and len(messages) > 4:
            messages = messages[-4:]
        
        # Adiciona novo prompt
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Chama modelo via aisuite
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.95,
                timeout=self.timeout
            )
            
            response_content = response.choices[0].message.content
            updated_history = history + [prompt, response_content]
            
            # Salva no histórico interno
            self._response_history.append({
                'prompt': prompt,
                'response': response_content,
                'model': self.model_name
            })
            
            return response_content, updated_history
            
        except Exception as e:
            error_msg = f"Erro na chamada LLM: {e}"
            return error_msg, history + [prompt, error_msg]
    
    def generate_initial_solution(self, problem: Dict) -> Tuple[str, List[str]]:
        """Gera solução inicial fraca para o problema"""
        prompt = self.prompts.get_prompt(
            'get_weak_answer',
            question=problem['description'],
            answer_format="Python code with function signature"
        )
        return self._call_llm(prompt)
    
    def generate_hints(self, problem: Dict, failed_code: str = "") -> str:
        """Gera hints para melhorar a solução"""
        if failed_code:
            prompt = self.prompts.get_prompt(
                'get_better_answer',
                question=problem['description'],
                previous_code=failed_code,
                hints="Think about edge cases and algorithm efficiency"
            )
        else:
            prompt = self.prompts.get_prompt(
                'get_weak_hints',
                question=problem['description']
            )
        
        response, _ = self._call_llm(prompt)
        return response
    
    def generate_improved_solution(self, problem: Dict, hints: str, current_code: str, history: List[str]) -> Tuple[str, List[str]]:
        """Gera solução melhorada baseada em hints"""
        prompt = self.prompts.get_prompt(
            'get_better_answer',
            question=problem['description'],
            previous_code=current_code,
            hints=hints
        )
        return self._call_llm(prompt, history)
    
    def calculate_reward(self, problem: Dict, code: str, test_results: List[bool], test_outputs: List[str]) -> float:
        """Calcula reward baseado na qualidade da solução"""
        test_summary = f"Passed: {sum(test_results)}/{len(test_results)} tests"
        if test_outputs:
            test_summary += f"\nOutputs: {test_outputs[:3]}"  # Primeiros 3 outputs
        
        prompt = self.prompts.get_prompt(
            'call_reward',
            question=problem['description'],
            code=code,
            test_results=test_summary
        )
        
        response, _ = self._call_llm(prompt)
        
        # Extrai score da resposta
        score_pattern = re.compile(r'[-+]?\d*\.?\d+')
        scores = score_pattern.findall(response)
        
        if scores:
            try:
                score = float(scores[-1])  # Pega último número encontrado
                # Garante que está no range [-100, 100]
                return max(-100.0, min(100.0, score))
            except ValueError:
                pass
        
        # Score padrão baseado nos testes se não conseguir extrair
        success_rate = sum(test_results) / len(test_results) if test_results else 0
        return -100 + (success_rate * 200)  # -100 a 100
    
    def generate_ground_truth_hints(self, problem: Dict, correct_answer: str) -> str:
        """Gera hints baseado na resposta correta (se disponível)"""
        prompt = self.prompts.get_prompt(
            'get_gt_hints',
            question=problem['description'],
            answer=correct_answer
        )
        response, _ = self._call_llm(prompt)
        return response
    
    def create_refinement_prompt(self, problem: Dict, current_code: str, issues: str) -> str:
        """Cria prompt específico para refinamento"""
        return self.prompts.get_prompt(
            'refine_prompt',
            question=problem['description'],
            current_code=current_code,
            issues=issues
        )
    
    def generate_bad_baseline(self, problem: Dict) -> Tuple[str, List[str]]:
        """Gera resposta intencionalmente ruim para baseline"""
        prompt = self.prompts.get_prompt('too_bad')
        return self._call_llm(prompt)
    
    def get_response_history(self) -> List[Dict]:
        """Retorna histórico de todas as respostas"""
        return self._response_history.copy()
    
    def clear_history(self):
        """Limpa histórico de respostas"""
        self._response_history = [] 