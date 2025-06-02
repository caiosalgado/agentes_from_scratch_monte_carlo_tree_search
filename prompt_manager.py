class PromptManager:
    def __init__(self):
        # Prompts base (defaults)
        self._prompts = {
            'get_weak_answer': """Question: {question}
The response should begin with [reasoning process]...[Verification]... and end with {answer_format}
Let's think step by step.""",

            'get_weak_hints': """Question: {question}
Could you provide me with the thought process to solve this problem, but please don't give me the answer or calculation, just the thought process?""",

            'get_better_answer': """Question: {question}
Previous attempt: {previous_code}
Hints for improvement: {hints}
Please provide a better solution considering the hints above.""",

            'get_gt_hints': """Question: {question}
Answer: {answer}
Please provide helpful hints about how to approach this problem.""",

            'call_reward': """Question: {question}
Code Solution: {code}
Test Results: {test_results}
Analyze this code solution strictly and provide a score between [-100, +100].
Response format: [Analysis]...[Score]...""",

            'refine_prompt': """Question: {question}
Current code: {current_code}
Issues found: {issues}
Please refine the code to fix these issues.""",

            'too_bad': """This is intentionally a bad response for baseline comparison.""",

            'hint_prompt': """Question: {question}
Provide strategic hints for solving this coding problem without giving away the solution."""
        }
        
        # Modificações aplicadas
        self._modifications = {key: {'before': '', 'after': '', 'replaced': False, 'replacement': ''} 
                              for key in self._prompts.keys()}
    
    def add_before(self, prompt_type: str, text: str):
        """Adiciona texto antes do prompt original"""
        if prompt_type not in self._prompts:
            raise ValueError(f"Prompt type '{prompt_type}' not found")
        self._modifications[prompt_type]['before'] = text
        return self
    
    def add_after(self, prompt_type: str, text: str):
        """Adiciona texto depois do prompt original"""
        if prompt_type not in self._prompts:
            raise ValueError(f"Prompt type '{prompt_type}' not found")
        self._modifications[prompt_type]['after'] = text
        return self
    
    def replace(self, prompt_type: str, new_prompt: str):
        """Substitui completamente o prompt"""
        if prompt_type not in self._prompts:
            raise ValueError(f"Prompt type '{prompt_type}' not found")
        self._modifications[prompt_type]['replaced'] = True
        self._modifications[prompt_type]['replacement'] = new_prompt
        return self
    
    def reset(self, prompt_type: str = None):
        """Reseta modificações (específica ou todas)"""
        if prompt_type:
            self._modifications[prompt_type] = {'before': '', 'after': '', 'replaced': False, 'replacement': ''}
        else:
            for key in self._modifications:
                self._modifications[key] = {'before': '', 'after': '', 'replaced': False, 'replacement': ''}
        return self
    
    def get_prompt(self, prompt_type: str, **kwargs) -> str:
        """Retorna o prompt final com modificações aplicadas"""
        if prompt_type not in self._prompts:
            raise ValueError(f"Prompt type '{prompt_type}' not found")
        
        mod = self._modifications[prompt_type]
        
        # Se foi substituído completamente
        if mod['replaced']:
            final_prompt = mod['replacement']
        else:
            # Monta: before + original + after
            original = self._prompts[prompt_type]
            final_prompt = f"{mod['before']}{original}{mod['after']}"
        
        # Aplica formatação com kwargs
        try:
            return final_prompt.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing parameter {e} for prompt '{prompt_type}'")
    
    def list_prompts(self):
        """Lista todos os tipos de prompt disponíveis"""
        return list(self._prompts.keys())
    
    def show_prompt(self, prompt_type: str):
        """Mostra o prompt final (sem formatação)"""
        mod = self._modifications[prompt_type]
        if mod['replaced']:
            return mod['replacement']
        else:
            return f"{mod['before']}{self._prompts[prompt_type]}{mod['after']}" 