import re
from typing import Optional


class AnswerValidator:
    """Validates and extracts answers from text responses."""
    
    def __init__(self):
        self.number_pattern = re.compile(r'\-?\d+\.\d+|\-?\d+')
    
    def extract_answer_label(self, text: str) -> Optional[str]:
        pass
    
    def is_answer_correct(self, ground_truth: str, predicted_answer: str) -> bool:
        pass
    
    def determine_answer_format(self, ground_truth: str) -> str:
        pass 