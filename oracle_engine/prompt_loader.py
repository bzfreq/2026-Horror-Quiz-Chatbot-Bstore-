"""
Prompt Loader Utility
Dynamically loads prompt templates from the prompts/ directory
"""
import os
from pathlib import Path


class PromptLoader:
    """
    Loads and manages prompt templates for the Horror Oracle LangGraph system.
    """
    
    def __init__(self, prompts_dir=None):
        """
        Initialize the prompt loader.
        
        Args:
            prompts_dir: Path to the prompts directory. If None, uses default location.
        """
        if prompts_dir is None:
            # Get the directory where this file is located
            current_dir = Path(__file__).parent
            self.prompts_dir = current_dir / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        # Cache for loaded prompts
        self._cache = {}
    
    def load_prompt(self, prompt_name: str) -> str:
        """
        Load a prompt template by name.
        
        Args:
            prompt_name: Name of the prompt file (without .txt extension)
            
        Returns:
            The prompt template as a string
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
        """
        # Check cache first
        if prompt_name in self._cache:
            return self._cache[prompt_name]
        
        # Construct file path
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        # Load and cache the prompt
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        self._cache[prompt_name] = prompt_content
        return prompt_content
    
    def reload_prompt(self, prompt_name: str) -> str:
        """
        Force reload a prompt from disk, bypassing cache.
        
        Args:
            prompt_name: Name of the prompt file (without .txt extension)
            
        Returns:
            The prompt template as a string
        """
        # Clear from cache if exists
        if prompt_name in self._cache:
            del self._cache[prompt_name]
        
        return self.load_prompt(prompt_name)
    
    def clear_cache(self):
        """Clear all cached prompts."""
        self._cache.clear()
    
    def get_available_prompts(self):
        """
        Get a list of all available prompt templates.
        
        Returns:
            List of prompt names (without .txt extension)
        """
        if not self.prompts_dir.exists():
            return []
        
        prompts = []
        for file in self.prompts_dir.glob("*.txt"):
            prompts.append(file.stem)
        
        return sorted(prompts)


# Singleton instance for easy access
_loader = PromptLoader()


def load_prompt(prompt_name: str) -> str:
    """
    Convenience function to load a prompt using the singleton loader.
    
    Args:
        prompt_name: Name of the prompt file (without .txt extension)
        
    Returns:
        The prompt template as a string
    """
    return _loader.load_prompt(prompt_name)


def reload_prompt(prompt_name: str) -> str:
    """
    Convenience function to reload a prompt using the singleton loader.
    
    Args:
        prompt_name: Name of the prompt file (without .txt extension)
        
    Returns:
        The prompt template as a string
    """
    return _loader.reload_prompt(prompt_name)


def get_available_prompts():
    """
    Convenience function to get available prompts.
    
    Returns:
        List of prompt names
    """
    return _loader.get_available_prompts()

