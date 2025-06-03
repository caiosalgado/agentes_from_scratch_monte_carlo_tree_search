class PromptManager:
    def __init__(self):
        # Prompts base (defaults)
        self._prompts = {
            'get_weak_answer': """📋 LEETCODE PROGRAMMING CHALLENGE

🎯 Problem: {title}

📝 Description:
{description}

⚠️ Constraints:
{constraints}

🔧 Function Signature (REQUIRED):
{function_signature}

📊 Test Cases:
{test_examples}

The response should begin with [reasoning process]...[Verification]... and end with {answer_format}
Let's think step by step.""",

            'get_weak_hints': """📋 LEETCODE PROGRAMMING CHALLENGE

🎯 Problem: {title}

📝 Description:
{description}

🔧 Function Signature:
{function_signature}

Could you provide me with the thought process to solve this problem, but please don't give me the answer or code, just the thought process?""",

            'get_better_answer': """📋 LEETCODE PROGRAMMING CHALLENGE

🎯 Problem: {title}

📝 Description:
{description}

🔧 Function Signature (REQUIRED):
{function_signature}

📊 Test Cases:
{test_examples}

Previous attempt: {previous_code}


📊 Test Results:
{test_results}

Hints for improvement: {hints}

Please refine your answer according to the hints.

The response should begin with [reasoning process]...

[verification]... and end with {answer_format}

Let's think step by step.""",

            'call_reward': """📋 LEETCODE PROGRAMMING CHALLENGE

🎯 Problem: {title}

📝 Description:
{description}

Code Solution: {code}
Test Results: {test_results}
Analyze this code solution Strictly and Critic, 
point out every flaw for ervery possible imperfect to minus every possible score! 
You need to be very harsh and mean in calculating grades, and never give full 
marks to ensure that the marks are authoritative. \n
Output a score between [-100,+100], ig. from -100 to +100. \n
Response format:\n[Analyst]...[Score]...""",

            'refine_prompt': """📋 LEETCODE PROGRAMMING CHALLENGE

🎯 Problem: {title}

📝 Description:
{description}

Current code: {current_code}
Test Results: {test_results}

Since we have a weak answer, could you provide a reflection or
feedback to improve this answer?

Please evaluate this answer strictly and critically, point out all flaws
and every possible intervention needed.""",

            'too_bad': """I don't know.""",

            'hint_prompt': """📋 LEETCODE PROGRAMMING CHALLENGE

📝 Description:
{description}

⚠️ Constraints:
{constraints}

🔧 Function Signature (REQUIRED):
{function_signature}

📊 Test Cases:
{test_examples}

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