#!/usr/bin/env python3
"""
Script de teste para verificar se todo o sistema MCTS está funcionando
"""

import traceback
from llm import LLM
from code_executor import CodeExecutor
from problems import Problems
from mcts import MCTS
from benchmark import run_benchmark, run_single_problem_benchmark, save_benchmark_results


def test_components():
    """Testa componentes individuais"""
    print("🧪 TESTANDO COMPONENTES INDIVIDUAIS")
    print("="*50)
    
    # Teste 1: PromptManager
    print("\n1️⃣ Testando PromptManager...")
    try:
        from prompt_manager import PromptManager
        pm = PromptManager()
        
        # Testa modificação de prompt
        pm.add_before('get_weak_answer', "You are an expert programmer. ")
        prompt = pm.get_prompt('get_weak_answer', question="Test question", answer_format="Python")
        print(f"✅ PromptManager OK - Prompt gerado: {len(prompt)} chars")
        
    except Exception as e:
        print(f"❌ PromptManager FALHOU: {e}")
        return False
    
    # Teste 2: CodeExecutor
    print("\n2️⃣ Testando CodeExecutor...")
    try:
        executor = CodeExecutor()
        
        # Testa extração de código
        sample_response = """
        Here's the solution:
        ```python
        def test_func(x):
            return x * 2
        ```
        """
        code = executor.extract_code(sample_response)
        print(f"✅ CodeExecutor extração OK - Código: {code[:50]}...")
        
        # Testa validação de sintaxe
        valid, error = executor.validate_syntax(code)
        print(f"✅ CodeExecutor validação OK - Válido: {valid}")
        
    except Exception as e:
        print(f"❌ CodeExecutor FALHOU: {e}")
        return False
    
    # Teste 3: Problems
    print("\n3️⃣ Testando Problems...")
    try:
        problems = Problems()
        all_problems = problems.load_json("leetcode_problems.json")
        print(f"✅ Problems OK - {len(all_problems)} problemas carregados")
        
        # Testa acesso por índice
        first_problem = problems[0]
        print(f"✅ Primeiro problema: {first_problem.get('title', 'Sem título')}")
        
    except Exception as e:
        print(f"❌ Problems FALHOU: {e}")
        return False
    
    # Teste 4: LLM (sem chamar modelo real)
    print("\n4️⃣ Testando LLM (setup apenas)...")
    try:
        llm = LLM()
        print(f"✅ LLM OK - Modelo: {llm.model_name}")
        print(f"✅ Prompts disponíveis: {len(llm.prompts.list_prompts())}")
        
    except Exception as e:
        print(f"❌ LLM FALHOU: {e}")
        return False
    
    print("\n✅ Todos os componentes básicos OK!")
    return True


def test_integration():
    """Testa integração entre componentes"""
    print("\n🔗 TESTANDO INTEGRAÇÃO")
    print("="*50)
    
    try:
        # Configura componentes
        llm = LLM()
        code_executor = CodeExecutor()
        problems = Problems()
        all_problems = problems.load_json("leetcode_problems.json")
        
        # Testa criação do MCTS
        mcts = MCTS(llm, code_executor, max_iter=2, max_child=2)  # Limites baixos para teste
        print("✅ MCTS criado com sucesso")
        
        # Testa modo debug (sem executar)
        first_problem = all_problems[0]
        print(f"✅ Problema selecionado: {first_problem.get('title')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integração FALHOU: {e}")
        traceback.print_exc()
        return False


def test_single_problem():
    """Testa execução em um único problema (modo debug)"""
    print("\n🎯 TESTANDO PROBLEMA ÚNICO (MODO DEBUG)")
    print("="*50)
    
    try:
        # Configura
        llm = LLM()
        code_executor = CodeExecutor()
        problems = Problems()
        all_problems = problems.load_json("leetcode_problems.json")
        
        # Seleciona problema mais simples
        test_problem = all_problems[0]  # isPalindrome
        print(f"🎯 Testando: {test_problem.get('title')}")
        
        # Cria MCTS com limites baixos
        mcts = MCTS(llm, code_executor, max_iter=3, max_child=2)
        
        # Entra em modo debug
        mcts.debug(test_problem)
        print("✅ Modo debug ativado")
        
        # Executa alguns steps
        print("\n🔄 Executando steps...")
        for i in range(2):  # Apenas 2 steps para teste
            if mcts.step():
                print(f"Step {i+1} executado")
            else:
                print("Execução parou (solução encontrada ou erro)")
                break
        
        # Verifica métricas
        metrics = mcts.metrics()
        print(f"✅ Métricas obtidas: {len(metrics)} campos")
        
        return True
        
    except Exception as e:
        print(f"❌ Teste problema único FALHOU: {e}")
        traceback.print_exc()
        return False


def test_benchmark_small():
    """Testa benchmark com poucos problemas"""
    print("\n📊 TESTANDO BENCHMARK PEQUENO")
    print("="*50)
    
    try:
        # Configura
        llm = LLM()
        code_executor = CodeExecutor()
        problems = Problems()
        all_problems = problems.load_json("leetcode_problems.json")
        
        # Seleciona apenas 2 primeiros problemas
        test_problems = all_problems[:2]
        print(f"🎯 Testando benchmark com {len(test_problems)} problemas")
        
        # Executa benchmark com limites baixos
        results = run_benchmark(
            problems=test_problems,
            llm=llm,
            code_executor=code_executor,
            max_iter=3,  # Poucos iterações para teste
            max_child=2,
            verbose=True
        )
        
        print(f"✅ Benchmark executado!")
        print(f"✅ Resultados: {len(results['individual_results'])} problemas")
        print(f"✅ Taxa de sucesso: {results['summary']['success_rate']:.1%}")
        
        # Salva resultados
        save_benchmark_results(results, "test_results.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Benchmark FALHOU: {e}")
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DO SISTEMA MCTS")
    print("="*60)
    
    tests = [
        ("Componentes", test_components),
        ("Integração", test_integration),
        ("Problema único", test_single_problem),
        ("Benchmark pequeno", test_benchmark_small)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ ERRO CRÍTICO em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📋 RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name:20} {status}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram ({passed/total:.1%})")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")


if __name__ == "__main__":
    main() 