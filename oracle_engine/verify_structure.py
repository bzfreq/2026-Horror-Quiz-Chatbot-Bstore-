"""
Simple structure verification script that doesn't require LangChain imports.
Checks that all files and prompts are in place.
"""
import os
from pathlib import Path


def verify_structure():
    """Verify that all required files and prompts are in place."""
    base_dir = Path(__file__).parent
    
    print("=" * 70)
    print("ORACLE ENGINE STRUCTURE VERIFICATION")
    print("=" * 70 + "\n")
    
    # Check node files
    print("1. Checking Node Files:")
    print("-" * 70)
    node_files = [
        "builder_node.py",
        "evaluator_node.py",
        "reward_node.py",
        "profile_node.py",
        "recommender_node.py",
        "lore_whisperer_node.py",
        "fear_meter_node.py"
    ]
    
    for node_file in node_files:
        file_path = base_dir / node_file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  [OK] {node_file:30s} ({size:,} bytes)")
        else:
            print(f"  [MISSING] {node_file:30s}")
    
    # Check prompt files
    print("\n2. Checking Prompt Template Files:")
    print("-" * 70)
    prompts_dir = base_dir / "prompts"
    
    if not prompts_dir.exists():
        print("  [MISSING] prompts/ directory!")
        return False
    
    prompt_files = [
        "question_generator_prompt.txt",
        "answer_evaluator_prompt.txt",
        "oracle_reactor_prompt.txt",
        "reward_generator_prompt.txt",
        "profile_updater_prompt.txt",
        "recommender_prompt.txt",
        "lore_whisperer_prompt.txt",
        "fear_meter_prompt.txt"
    ]
    
    for prompt_file in prompt_files:
        file_path = prompts_dir / prompt_file
        if file_path.exists():
            size = file_path.stat().st_size
            status = "Ready for content" if size < 200 else "Has content"
            print(f"  [OK] {prompt_file:35s} ({size:,} bytes) - {status}")
        else:
            print(f"  [MISSING] {prompt_file:35s}")
    
    # Check utility files
    print("\n3. Checking Utility Files:")
    print("-" * 70)
    utility_files = [
        "prompt_loader.py",
        "__init__.py",
        "main.py",
        "README.md",
        "NODE_PROMPT_MAPPING.md"
    ]
    
    for util_file in utility_files:
        file_path = base_dir / util_file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  [OK] {util_file:35s} ({size:,} bytes)")
        else:
            print(f"  [MISSING] {util_file:35s}")
    
    # Check prompt loader functionality (without importing)
    print("\n4. Checking Prompt Loader Contents:")
    print("-" * 70)
    loader_path = base_dir / "prompt_loader.py"
    if loader_path.exists():
        with open(loader_path, 'r', encoding='utf-8') as f:
            content = f.read()
            features = {
                "PromptLoader class": "class PromptLoader" in content,
                "load_prompt function": "def load_prompt" in content,
                "reload_prompt function": "def reload_prompt" in content,
                "get_available_prompts function": "def get_available_prompts" in content,
                "Caching mechanism": "_cache" in content
            }
            
            for feature, present in features.items():
                status = "[OK]" if present else "[MISSING]"
                print(f"  {status} {feature}")
    
    # Check __init__.py exports
    print("\n5. Checking Package Exports:")
    print("-" * 70)
    init_path = base_dir / "__init__.py"
    if init_path.exists():
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
            exports = {
                "load_prompt": "load_prompt" in content,
                "BuilderNode": "BuilderNode" in content,
                "EvaluatorNode": "EvaluatorNode" in content,
                "RewardNode": "RewardNode" in content,
                "ProfileNode": "ProfileNode" in content,
                "RecommenderNode": "RecommenderNode" in content,
                "LoreWhispererNode": "LoreWhispererNode" in content,
                "FearMeterNode": "FearMeterNode" in content
            }
            
            for export, present in exports.items():
                status = "[OK]" if present else "[MISSING]"
                print(f"  {status} {export}")
    
    # Node to Prompt Mapping
    print("\n6. Node -> Prompt Mapping:")
    print("-" * 70)
    mappings = [
        ("builder_node.py", "question_generator_prompt.txt"),
        ("evaluator_node.py", "answer_evaluator_prompt.txt + oracle_reactor_prompt.txt"),
        ("reward_node.py", "reward_generator_prompt.txt"),
        ("profile_node.py", "profile_updater_prompt.txt"),
        ("recommender_node.py", "recommender_prompt.txt"),
        ("lore_whisperer_node.py", "lore_whisperer_prompt.txt"),
        ("fear_meter_node.py", "fear_meter_prompt.txt")
    ]
    
    for node, prompt in mappings:
        print(f"  {node:30s} -> {prompt}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_nodes_exist = all((base_dir / nf).exists() for nf in node_files)
    all_prompts_exist = all((prompts_dir / pf).exists() for pf in prompt_files)
    all_utils_exist = all((base_dir / uf).exists() for uf in utility_files)
    
    if all_nodes_exist and all_prompts_exist and all_utils_exist:
        print("[SUCCESS] ALL FILES IN PLACE!")
        print("[SUCCESS] Structure is ready for prompt content")
        print("\nNext Steps:")
        print("  1. Fill in the 8 prompt template files with actual content")
        print("  2. Test each node with the completed prompts")
        print("  3. Integrate nodes into LangGraph workflow")
        return True
    else:
        print("[ERROR] SOME FILES ARE MISSING!")
        print("Please ensure all required files are created.")
        return False


if __name__ == "__main__":
    success = verify_structure()
    exit(0 if success else 1)

