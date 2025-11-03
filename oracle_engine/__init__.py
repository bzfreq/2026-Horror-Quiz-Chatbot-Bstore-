"""
Horror Oracle Engine - LangGraph-powered quiz system

This module provides a sophisticated quiz system that uses LangGraph
to orchestrate multiple nodes for generating, evaluating, and personalizing
horror movie quizzes.
"""

from oracle_engine.prompt_loader import load_prompt, reload_prompt, get_available_prompts

# Node imports
from oracle_engine.builder_node import BuilderNode, create_builder_node
from oracle_engine.evaluator_node import EvaluatorNode, create_evaluator_node
from oracle_engine.reward_node import RewardNode, create_reward_node
from oracle_engine.profile_node import ProfileNode, create_profile_node
from oracle_engine.recommender_node import RecommenderNode, create_recommender_node
from oracle_engine.lore_whisperer_node import LoreWhispererNode, create_lore_node
from oracle_engine.fear_meter_node import FearMeterNode, create_fear_meter_node

# Main interface (keeping backward compatibility)
from oracle_engine.main import start_first_quiz, evaluate_and_progress

__all__ = [
    # Prompt utilities
    'load_prompt',
    'reload_prompt',
    'get_available_prompts',
    
    # Node classes
    'BuilderNode',
    'EvaluatorNode',
    'RewardNode',
    'ProfileNode',
    'RecommenderNode',
    'LoreWhispererNode',
    'FearMeterNode',
    
    # Factory functions
    'create_builder_node',
    'create_evaluator_node',
    'create_reward_node',
    'create_profile_node',
    'create_recommender_node',
    'create_lore_node',
    'create_fear_meter_node',
    
    # Main interface
    'start_first_quiz',
    'evaluate_and_progress',
]

__version__ = '0.2.0'

