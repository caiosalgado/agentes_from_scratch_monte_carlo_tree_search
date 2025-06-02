from typing import Optional, List, Tuple


class LLMInterface:
    """Interface for all LLM interactions in the MCTS refinement process."""
    
    def __init__(self, client, model_name: str = "ollama:qwen3:14b"):
        self.client = client
        self.model_name = model_name
        self.timeout = 150
    
    def generate_weak_answer(self, question: str, answer_format: str = "") -> Tuple[str, List[str]]:
        pass
    
    def generate_weak_hints(self, question: str) -> str:
        pass
    
    def generate_better_answer(self, question: str, hints: str, history: List[str]) -> Tuple[str, List[str]]:
        pass
    
    def generate_ground_truth_hints(self, question: str, answer: str) -> str:
        pass
    
    def calculate_reward_score(self, question: str, answer: str) -> float:
        pass
    
    def create_refinement_prompt(self, question: str, current_answer: str, hints: str) -> str:
        pass
    
    def generate_bad_baseline_answer(self, question: str) -> str:
        pass
    
    def create_hint_prompt(self, question: str) -> str:
        pass
    
    def _generate_response(self, prompt: str, history: Optional[List[str]] = None, truncate: bool = True) -> Tuple[str, List[str]]:
        pass 