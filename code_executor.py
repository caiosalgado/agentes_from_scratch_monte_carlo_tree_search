import re
import sys
import io
import ast
import time
import contextlib
import subprocess
from typing import List, Dict, Any, Tuple
import tempfile
import os


class CodeExecutor:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.code_pattern = re.compile(r'```python\n(.*?)\n```', re.DOTALL)
        self.function_pattern = re.compile(r'def\s+(\w+)\s*\([^)]*\):', re.MULTILINE)
    
    def extract_code(self, llm_response: str) -> str:
        """Extrai código Python da resposta do LLM"""
        # Primeiro tenta encontrar código em blocos ```python
        matches = self.code_pattern.findall(llm_response)
        if matches:
            return matches[0].strip()
        
        # Se não encontrar, procura por funções def
        lines = llm_response.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if 'def ' in line and '(' in line and ')' in line:
                in_code_block = True
                code_lines.append(line)
            elif in_code_block:
                if line.strip() == '' or line.startswith('    ') or line.startswith('\t'):
                    code_lines.append(line)
                else:
                    break
        
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        # Último recurso: retorna a resposta completa se parecer código
        if 'def ' in llm_response and 'return' in llm_response:
            return llm_response.strip()
        
        return ""
    
    def validate_syntax(self, code: str) -> Tuple[bool, str]:
        """Valida sintaxe do código Python"""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"
        except Exception as e:
            return False, f"Parse Error: {e}"
    
    def execute_safely(self, code: str, test_cases: List[Dict]) -> Tuple[List[bool], List[str], str]:
        """Executa código de forma segura com casos de teste"""
        syntax_valid, error_msg = self.validate_syntax(code)
        if not syntax_valid:
            return [False] * len(test_cases), [error_msg] * len(test_cases), error_msg
        
        # Encontra o nome da função principal
        function_matches = self.function_pattern.findall(code)
        if not function_matches:
            error = "No function definition found"
            return [False] * len(test_cases), [error] * len(test_cases), error
        
        function_name = function_matches[0]
        results = []
        outputs = []
        
        for test_case in test_cases:
            try:
                result, output = self._run_single_test(code, function_name, test_case)
                results.append(result)
                outputs.append(output)
            except Exception as e:
                results.append(False)
                outputs.append(f"Execution error: {e}")
        
        overall_error = "" if any(results) else "All tests failed"
        return results, outputs, overall_error
    
    def _run_single_test(self, code: str, function_name: str, test_case: Dict) -> Tuple[bool, str]:
        """Executa um único caso de teste"""
        test_input = test_case.get('input', [])
        expected = test_case.get('expected')
        
        # Prepara código de teste
        test_code = f"""
{code}

# Importações necessárias
from typing import List, Optional

# Executa teste
try:
    inputs = {test_input}
    if isinstance(inputs, list) and len(inputs) > 0:
        if len(inputs) == 1:
            result = {function_name}(inputs[0])
        else:
            result = {function_name}(*inputs)
    else:
        result = {function_name}()
    
    expected = {expected}
    
    # Compara resultados
    if result == expected:
        print("PASS")
    else:
        print(f"FAIL: expected {{expected}}, got {{result}}")
        
except Exception as e:
    print(f"ERROR: {{e}}")
"""
        
        # Executa em processo separado para segurança
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_code)
                temp_file = f.name
            
            # Executa com timeout
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            output = result.stdout.strip()
            
            # Limpa arquivo temporário
            try:
                os.unlink(temp_file)
            except:
                pass
            
            if result.returncode != 0:
                return False, f"Runtime error: {result.stderr}"
            
            return output == "PASS", output
            
        except subprocess.TimeoutExpired:
            return False, "Timeout exceeded"
        except Exception as e:
            return False, f"Execution failed: {e}"
    
    def calculate_score(self, test_results: List[bool]) -> float:
        """Calcula score baseado nos resultados dos testes"""
        if not test_results:
            return -100.0
        
        success_rate = sum(test_results) / len(test_results)
        
        # Score de -100 a +100
        if success_rate == 1.0:
            return 100.0
        elif success_rate >= 0.8:
            return 50.0 + (success_rate - 0.8) * 250  # 50 a 100
        elif success_rate >= 0.5:
            return 0.0 + (success_rate - 0.5) * 166.67  # 0 a 50
        else:
            return -100.0 + success_rate * 200  # -100 a 0
    
    def run_tests(self, code: str, test_cases: List[Dict]) -> Dict:
        """Executa todos os testes e retorna resultado completo"""
        if not code.strip():
            return {
                'success': False,
                'test_results': [False] * len(test_cases),
                'test_outputs': ['No code provided'] * len(test_cases),
                'score': -100.0,
                'error': 'No code provided'
            }
        
        test_results, test_outputs, error = self.execute_safely(code, test_cases)
        score = self.calculate_score(test_results)
        
        return {
            'success': all(test_results),
            'test_results': test_results,
            'test_outputs': test_outputs,
            'score': score,
            'error': error,
            'success_rate': sum(test_results) / len(test_results) if test_results else 0.0
        } 