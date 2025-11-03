"""
Simple structure test for Builder and Evaluator nodes
Tests the fallback logic without requiring LangChain/OpenAI
"""
import sys
import json
import os

# Add parent directory to path to import backend module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_prompt_files():
    """Test that prompt files exist and are properly formatted."""
    print("\n" + "="*60)
    print("TESTING PROMPT FILES")
    print("="*60)
    
    try:
        from prompt_loader import load_prompt
        
        # Test question generator prompt
        print("\n--- Testing question_generator_prompt.txt ---")
        qg_prompt = load_prompt("question_generator_prompt")
        assert len(qg_prompt) > 100, "Question generator prompt seems too short"
        assert "{theme}" in qg_prompt, "Prompt missing {theme} placeholder"
        assert "{difficulty}" in qg_prompt, "Prompt missing {difficulty} placeholder"
        assert "{tone}" in qg_prompt, "Prompt missing {tone} placeholder"
        print("[OK] Question Generator Prompt: Valid")
        
        # Test answer evaluator prompt
        print("\n--- Testing answer_evaluator_prompt.txt ---")
        ae_prompt = load_prompt("answer_evaluator_prompt")
        assert len(ae_prompt) > 100, "Answer evaluator prompt seems too short"
        assert "{tone}" in ae_prompt, "Prompt missing {tone} placeholder"
        assert "{score}" in ae_prompt, "Prompt missing {score} placeholder"
        assert "{total}" in ae_prompt, "Prompt missing {total} placeholder"
        print("[OK] Answer Evaluator Prompt: Valid")
        
        print("\n" + "="*60)
        print("PROMPT FILES: ALL VALID")
        print("="*60)
        
    except Exception as e:
        print(f"[ERROR] Testing prompts: {e}")
        raise


def test_builder_structure():
    """Test Builder node structure (without LLM)."""
    print("\n" + "="*60)
    print("TESTING BUILDER NODE STRUCTURE")
    print("="*60)
    
    # Mock Config to avoid API key requirements
    import backend.config as config_module
    original_validate = config_module.Config.validate
    config_module.Config.validate = lambda: None
    config_module.Config.OPENAI_API_KEY = None
    
    try:
        from builder_node import BuilderNode
        
        print("\n--- Creating Builder Node ---")
        builder = BuilderNode()
        print("[OK] Builder Node Created")
        
        print("\n--- Testing generate_questions (fallback mode) ---")
        questions = builder.generate_questions(
            theme="slasher",
            difficulty=0.5,
            tone="creepy"
        )
        
        assert len(questions) == 5, f"Should generate 5 questions, got {len(questions)}"
        print(f"[OK] Generated {len(questions)} questions")
        
        # Validate structure of first question
        q = questions[0]
        required_fields = ["question", "choices", "correct_answer", "difficulty", "tone", "theme"]
        for field in required_fields:
            assert field in q, f"Question missing required field: {field}"
        
        assert len(q["choices"]) == 4, f"Should have 4 choices, got {len(q['choices'])}"
        assert q["correct_answer"] in q["choices"], "correct_answer not in choices"
        
        print("[OK] Question structure valid:")
        print(f"   - Question: {q['question'][:50]}...")
        print(f"   - Choices: {len(q['choices'])}")
        print(f"   - Has correct_answer: Yes")
        print(f"   - Difficulty: {q['difficulty']}")
        print(f"   - Tone: {q['tone']}")
        print(f"   - Theme: {q['theme']}")
        
        print("\n--- Testing generate_quiz ---")
        quiz = builder.generate_quiz(
            difficulty="intermediate",
            theme="monster"
        )
        
        required_quiz_fields = ["room", "intro", "questions", "theme", "difficulty"]
        for field in required_quiz_fields:
            assert field in quiz, f"Quiz missing required field: {field}"
        
        assert len(quiz["questions"]) == 5, "Quiz should have 5 questions"
        
        print("[OK] Quiz structure valid:")
        print(f"   - Room: {quiz['room']}")
        print(f"   - Intro: {quiz['intro'][:50]}...")
        print(f"   - Questions: {len(quiz['questions'])}")
        print(f"   - Theme: {quiz['theme']}")
        
        print("\n" + "="*60)
        print("BUILDER NODE STRUCTURE: VALID")
        print("="*60)
        
        return quiz
        
    finally:
        config_module.Config.validate = original_validate


def test_evaluator_structure(quiz):
    """Test Evaluator node structure (without LLM)."""
    print("\n" + "="*60)
    print("TESTING EVALUATOR NODE STRUCTURE")
    print("="*60)
    
    # Mock Config to avoid API key requirements
    import backend.config as config_module
    original_validate = config_module.Config.validate
    config_module.Config.validate = lambda: None
    config_module.Config.OPENAI_API_KEY = None
    
    try:
        from evaluator_node import EvaluatorNode
        
        print("\n--- Creating Evaluator Node ---")
        evaluator = EvaluatorNode()
        print("[OK] Evaluator Node Created")
        
        questions = quiz["questions"]
        
        # Test perfect score
        print("\n--- Testing Perfect Score (5/5) ---")
        perfect_answers = {q["question"]: q["correct_answer"] for q in questions}
        
        result = evaluator.evaluate_answers(
            questions=questions,
            player_answers=perfect_answers,
            tone="creepy"
        )
        
        required_fields = [
            "score", "total", "percentage", "grade", "verdict",
            "detailed_feedback", "oracle_reaction", "next_action"
        ]
        for field in required_fields:
            assert field in result, f"Result missing required field: {field}"
        
        assert result["score"] == 5, f"Expected score 5, got {result['score']}"
        assert result["total"] == 5, f"Expected total 5, got {result['total']}"
        assert result["percentage"] == 100.0, f"Expected 100%, got {result['percentage']}"
        assert result["grade"] == "S", f"Expected grade S, got {result['grade']}"
        assert result["next_action"] == "advance", f"Expected 'advance', got {result['next_action']}"
        assert result["unlocked_lore"] is not None, "Perfect score should unlock lore"
        
        print("[OK] Perfect score result valid:")
        print(f"   - Score: {result['score']}/{result['total']}")
        print(f"   - Percentage: {result['percentage']}%")
        print(f"   - Grade: {result['grade']}")
        print(f"   - Next Action: {result['next_action']}")
        print(f"   - Verdict: {result['verdict']}")
        print(f"   - Oracle Reaction: {result['oracle_reaction'][:80]}...")
        print(f"   - Unlocked Lore: Yes")
        
        # Test partial score
        print("\n--- Testing Partial Score (3/5) ---")
        partial_answers = {
            questions[0]["question"]: questions[0]["correct_answer"],
            questions[1]["question"]: questions[1]["correct_answer"],
            questions[2]["question"]: questions[2]["correct_answer"],
            questions[3]["question"]: "Wrong Answer",
            questions[4]["question"]: "Wrong Answer"
        }
        
        result = evaluator.evaluate_answers(
            questions=questions,
            player_answers=partial_answers,
            tone="mocking"
        )
        
        assert result["score"] == 3, f"Expected score 3, got {result['score']}"
        assert 50 <= result["percentage"] <= 70, f"Expected ~60%, got {result['percentage']}"
        
        print("[OK] Partial score result valid:")
        print(f"   - Score: {result['score']}/{result['total']}")
        print(f"   - Percentage: {result['percentage']}%")
        print(f"   - Grade: {result['grade']}")
        print(f"   - Next Action: {result['next_action']}")
        
        # Test different tones
        print("\n--- Testing Different Tones ---")
        tones = ["creepy", "mocking", "ancient", "whispered", "grim", "playful"]
        
        for tone in tones:
            reaction = evaluator.generate_oracle_reaction(
                score=3,
                total=5,
                context={"tone": tone}
            )
            assert len(reaction) > 0, f"Reaction for {tone} is empty"
            print(f"[OK] {tone.capitalize()} tone: \"{reaction[:60]}...\"")
        
        print("\n" + "="*60)
        print("EVALUATOR NODE STRUCTURE: VALID")
        print("="*60)
        
    finally:
        config_module.Config.validate = original_validate


def main():
    """Run all structure tests."""
    print("\n" + "="*60)
    print("ORACLE ENGINE: STRUCTURE VALIDATION")
    print("="*60)
    print("\nTesting without LangChain/OpenAI (using fallback logic)")
    
    try:
        # Test prompts
        test_prompt_files()
        
        # Test Builder
        quiz = test_builder_structure()
        
        # Test Evaluator
        test_evaluator_structure(quiz)
        
        print("\n" + "="*60)
        print("ALL STRUCTURE TESTS PASSED!")
        print("="*60)
        print("\nSUMMARY:")
        print("   1. Question Generator Prompt: Valid")
        print("   2. Answer Evaluator Prompt: Valid")
        print("   3. Builder Node: Generates 5 structured questions")
        print("   4. Evaluator Node: Scores & provides atmospheric feedback")
        print("   5. Fallback logic: Works without LLM")
        print("\nNEXT STEPS:")
        print("   - Both nodes are ready for integration")
        print("   - Will use LLM when API keys are available")
        print("   - Falls back to hardcoded logic when LLM unavailable")
        print("   - No Flask or frontend changes needed yet")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

