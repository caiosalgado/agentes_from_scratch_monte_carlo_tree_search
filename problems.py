import json
import random
from typing import List, Dict, Any, Optional


class Problems:
    def __init__(self):
        self.problems: List[Dict] = []
        self._loaded_file = None
    
    def load_json(self, file_path: str) -> List[Dict]:
        """Carrega problemas do arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'problems' in data:
                self.problems = data['problems']
            else:
                self.problems = data if isinstance(data, list) else [data]
            
            self._loaded_file = file_path
            print(f"✅ Carregados {len(self.problems)} problemas de {file_path}")
            return self.problems
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo {file_path} não encontrado")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON: {e}")
        except Exception as e:
            raise Exception(f"Erro ao carregar problemas: {e}")
    
    def get_by_id(self, problem_id: str) -> Optional[Dict]:
        """Busca problema por ID"""
        for problem in self.problems:
            if problem.get('id') == problem_id:
                return problem
        return None
    
    def get_by_index(self, index: int) -> Optional[Dict]:
        """Busca problema por índice"""
        if 0 <= index < len(self.problems):
            return self.problems[index]
        return None
    
    def random_sample(self, n: int = 1) -> List[Dict]:
        """Retorna amostra aleatória de problemas"""
        if n >= len(self.problems):
            return self.problems.copy()
        return random.sample(self.problems, n)
    
    def filter_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Filtra problemas por dificuldade (se disponível)"""
        return [p for p in self.problems if p.get('difficulty', '').lower() == difficulty.lower()]
    
    def list_ids(self) -> List[str]:
        """Lista todos os IDs de problemas"""
        return [p.get('id', f"problem_{i}") for i, p in enumerate(self.problems)]
    
    def list_titles(self) -> List[str]:
        """Lista todos os títulos de problemas"""
        return [p.get('title', f"Problem {i+1}") for i, p in enumerate(self.problems)]
    
    def validate_problem(self, problem: Dict) -> bool:
        """Valida se um problema tem os campos necessários"""
        required_fields = ['id', 'title', 'description', 'tests']
        return all(field in problem for field in required_fields)
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas dos problemas carregados"""
        if not self.problems:
            return {'total': 0, 'valid': 0, 'invalid': 0}
        
        valid_count = sum(1 for p in self.problems if self.validate_problem(p))
        
        return {
            'total': len(self.problems),
            'valid': valid_count,
            'invalid': len(self.problems) - valid_count,
            'source_file': self._loaded_file
        }
    
    def __len__(self) -> int:
        return len(self.problems)
    
    def __getitem__(self, index: int) -> Dict:
        return self.problems[index]
    
    def __iter__(self):
        return iter(self.problems) 