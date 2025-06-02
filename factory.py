from mcts_algorithm import MCTSRefinementAlgorithm
from llm_interface import LLMInterface


def create_mcts_algorithm(client, model_name: str = "ollama:qwen3:14b", max_iterations: int = 16) -> MCTSRefinementAlgorithm:
    """
    Factory function to create a complete MCTS refinement algorithm instance.
    
    Args:
        client: The LLM client (e.g., aisuite client)
        model_name: Name of the model to use
        max_iterations: Maximum number of MCTS iterations
        
    Returns:
        MCTSRefinementAlgorithm: Configured algorithm instance
    """
    llm_interface = LLMInterface(client, model_name)
    return MCTSRefinementAlgorithm(llm_interface, max_iterations) 