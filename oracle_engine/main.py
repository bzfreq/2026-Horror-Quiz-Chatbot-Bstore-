import json
from oracle_engine.fear_meter_node import FearMeterNode
from oracle_engine.builder_node import BuilderNode
from oracle_engine.evaluator_node import EvaluatorNode
from oracle_engine.reward_node import RewardNode
from oracle_engine.profile_node import ProfileNode
from oracle_engine.recommender_node import RecommenderNode
from oracle_engine.lore_whisperer_node import LoreWhispererNode

# === Horror Oracle LangGraph - Full Chain Implementation ===

def start_first_quiz(user_id: str):
    """
    Starts the first horror quiz - FULL CHAIN:
    Builder → Profile → Lore → Fear Meter
    
    Returns a complete quiz with atmospheric elements.
    """
    import time
    start_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"[ORACLE ENGINE] Starting quiz for user: {user_id}")
    print(f"⏱️  start_first_quiz started at 0.000s")
    print(f"{'='*60}")
    
    # Initialize nodes
    t0 = time.time()
    builder = BuilderNode()
    profile_node = ProfileNode()
    lore_node = LoreWhispererNode()
    fear_meter = FearMeterNode()
    print(f"⏱️  Nodes initialized: {time.time() - t0:.3f}s")
    
    import random
    
    # Randomize seed for variety
    random.seed(time.time())
    
    # 1. Get user profile (or create default)
    print("[1/4] Loading user profile...")
    t1 = time.time()
    user_profile = profile_node.get_profile(user_id)
    
    # Try to load context from disk to merge with profile
    try:
        from oracle_engine.memory import TemporaryMemory
        context_data = TemporaryMemory.load_context(user_id)
        if context_data and "player_profile" in context_data:
            # Merge saved profile data with current profile
            saved_profile = context_data["player_profile"]
            user_profile.update(saved_profile)
            print(f"[OK] Merged saved context with profile")
    except Exception as e:
        print(f"[WARN] Failed to load context: {e}")
    
    print(f"⏱️  Profile loaded: {time.time() - t1:.3f}s")
    if not user_profile.get("name"):
        user_profile = {
            "user_id": user_id,
            "name": user_id,
            "bravery": 50,
            "lore_knowledge": 50,
            "logic": 50,
            "fear_level": 50,
            "difficulty_level": "intermediate",
            "preferred_themes": [],
            "favorite_theme": "general_horror",
            "preferred_tone": "creepy"
        }
    
    # Pick a randomized theme for variety (even on first quiz)
    all_themes = [
        "general_horror", "slasher", "psychological", "supernatural",
        "zombie", "vampire", "cosmic", "gothic", "body_horror",
        "found_footage", "haunted_house", "folklore", "survival"
    ]
    
    # 60% chance to use favorite theme, 40% chance for random theme
    if user_profile.get("favorite_theme") and random.random() < 0.6:
        selected_theme = user_profile.get("favorite_theme", "general_horror")
    else:
        selected_theme = random.choice(all_themes)
    
    print(f"[THEME] Selected theme for this quiz: {selected_theme}")
    
    # 2. Generate quiz using Builder Node
    print("[2/4] Generating quiz questions...")
    t2 = time.time()
    quiz_data = builder.generate_quiz(
        user_profile=user_profile,
        difficulty=user_profile.get("difficulty_level", "intermediate"),
        theme=selected_theme
    )
    print(f"⏱️  ⚡ QUIZ GENERATION (LLM call): {time.time() - t2:.3f}s ⚡")
    
    # 3. Generate atmospheric lore
    print("[3/4] Whispering lore...")
    t3 = time.time()
    lore_context = {
        "user_profile": user_profile,
        "theme": quiz_data.get("theme", "horror"),
        "emotion": "indifferent",  # Initial state
        "performance": "beginning"
    }
    lore_output = lore_node.generate_lore(lore_context)
    print(f"⏱️  Lore generated: {time.time() - t3:.3f}s")
    
    # 4. Initialize fear meter state
    print("[4/4] Calibrating fear meter...")
    t4 = time.time()
    initial_state = fear_meter.translate_to_oracle_state(
        accuracy=0.5,  # Neutral starting point
        previous_tone="neutral",
        player_profile=user_profile
    )
    print(f"⏱️  Fear meter calibrated: {time.time() - t4:.3f}s")
    
    # Compile full response
    response = {
        "user_id": user_id,
        "room": quiz_data.get("room", "The First Chamber"),
        "intro": quiz_data.get("intro", "The Oracle awaits..."),
        "questions": quiz_data.get("questions", []),
        "theme": quiz_data.get("theme"),
        "difficulty": quiz_data.get("difficulty"),
        "tone": quiz_data.get("tone"),
        "lore": lore_output,
        "oracle_state": {
            "tone": initial_state["oracle_tone"],
            "emotion": initial_state["oracle_emotion"],
            "intensity": initial_state["intensity"]
        },
        "player_profile": user_profile
    }
    
    total_time = time.time() - start_time
    print(f"[OK] Quiz generated | Theme: {quiz_data.get('theme')} | Difficulty: {quiz_data.get('difficulty')}")
    print(f"⏱️  ⭐ TOTAL start_first_quiz TIME: {total_time:.3f}s ⭐")
    print(f"{'='*60}\n")
    
    return response


def evaluate_and_progress(user_id: str, quiz: dict, answers: dict, 
                         player_profile: dict = None, previous_tone: str = "neutral"):
    """
    Evaluates quiz answers and runs the FULL CHAIN:
    Evaluator → Reactor → Fear Meter → Reward → Profile → Recommender → Lore
    
    Args:
        user_id: Player identifier
        quiz: Quiz data with questions
        answers: Player's submitted answers
        player_profile: Player's profile data (optional)
        previous_tone: Oracle's tone from last interaction (optional)
    
    Returns:
        Complete evaluation with Oracle state, rewards, recommendations, and lore
    """
    print(f"\n{'='*60}")
    print(f"[ORACLE ENGINE] Evaluating answers for user: {user_id}")
    print(f"{'='*60}")
    
    # Initialize all nodes
    evaluator = EvaluatorNode()
    fear_meter = FearMeterNode()
    reward_node = RewardNode()
    profile_node = ProfileNode()
    recommender = RecommenderNode()
    lore_node = LoreWhispererNode()
    
    # Default player profile if not provided
    if player_profile is None:
        player_profile = {
            "name": user_id,
            "bravery": 50,
            "lore_knowledge": 50,
            "logic": 50,
            "fear_level": 50
        }
    
    # 1. EVALUATOR NODE - Evaluate answers and generate Oracle reaction
    print("[1/7] Evaluating answers...")
    questions = quiz.get("questions", [])
    tone = quiz.get("tone", "creepy")
    
    evaluation = evaluator.evaluate_answers(
        questions=questions,
        player_answers=answers,
        tone=tone
    )
    
    score = evaluation["score"]
    total = evaluation["total"]
    accuracy = score / total if total > 0 else 0.0
    
    print(f"[OK] Score: {score}/{total} ({accuracy*100:.1f}%)")
    
    # 2. REACTOR (part of Fear Meter) - Translate to Oracle emotional state
    print("[2/7] Oracle reacts to performance...")
    oracle_state = fear_meter.translate_to_oracle_state(
        accuracy=accuracy,
        previous_tone=previous_tone,
        player_profile=player_profile
    )
    
    print(f"[OK] Oracle Emotion: {oracle_state['oracle_emotion']} | Tone: {oracle_state['oracle_tone']}")
    
    # 3. REWARD NODE - Generate rewards based on performance
    print("[3/7] Generating rewards...")
    performance_data = {
        "score": score,
        "out_of": total,
        "accuracy": accuracy,
        "grade": evaluation.get("grade", "C")
    }
    
    # Add Oracle state to player profile for reward generation
    player_profile_with_oracle = player_profile.copy()
    player_profile_with_oracle["oracle_emotion"] = oracle_state["oracle_emotion"]
    player_profile_with_oracle["oracle_tone"] = oracle_state["oracle_tone"]
    
    rewards = reward_node.generate_rewards(
        performance=performance_data,
        user_profile=player_profile_with_oracle
    )
    
    print(f"[OK] Rewards generated")
    
    # 4. PROFILE NODE - Update user profile
    print("[4/7] Updating player profile...")
    quiz_metadata = {
        "theme": quiz.get("theme", "general_horror"),
        "difficulty": quiz.get("difficulty", "intermediate"),
        "tone": tone
    }
    
    updated_profile = profile_node.update_profile(
        user_id=user_id,
        performance_data=performance_data,
        quiz_metadata=quiz_metadata
    )
    
    # Merge with oracle state updates
    updated_profile["fear_level"] = oracle_state["player_state"]["fear_level"]
    updated_profile["confidence"] = oracle_state["player_state"]["confidence"]
    
    print(f"[OK] Profile updated | Fear Level: {updated_profile['fear_level']}")
    
    # 5. RECOMMENDER NODE - Generate movie recommendations
    print("[5/7] Generating movie recommendations...")
    context = {
        "recent_quiz_theme": quiz.get("theme"),
        "performance": "excellent" if accuracy >= 0.8 else "good" if accuracy >= 0.6 else "average",
        "oracle_emotion": oracle_state["oracle_emotion"]
    }
    
    recommendations = recommender.recommend_movies(
        user_profile=updated_profile,
        context=context
    )
    
    print(f"[OK] Recommendations generated: {len(recommendations)} movies")
    
    # 6. LORE NODE - Generate atmospheric transition lore
    print("[6/7] Whispering transition lore...")
    lore_output = lore_node.whisper_between_chambers(
        player_profile=updated_profile,
        last_theme=quiz.get("theme", "horror"),
        emotion=oracle_state["oracle_emotion"],
        performance="excellent" if accuracy >= 0.8 else "poor" if accuracy < 0.4 else "average"
    )
    
    print(f"[OK] Lore fragment generated")
    
    # 7. FEAR METER - Final state compilation
    print("[7/7] Compiling final state...")
    
    # 8. PICK NEXT DIFFICULTY AND THEME - For next quiz session
    current_difficulty = quiz.get("difficulty", "intermediate")
    current_theme = quiz.get("theme", "general_horror")
    next_difficulty, next_theme = pick_next_difficulty_and_theme(
        accuracy=accuracy,
        current_difficulty=current_difficulty,
        current_theme=current_theme,
        player_profile=updated_profile
    )
    
    # Compile complete response
    response = {
        "user_id": user_id,
        "score": score,
        "out_of": total,
        "accuracy": accuracy,
        "percentage": round(accuracy * 100, 1),
        
        # Evaluation results
        "evaluation": {
            "grade": evaluation.get("grade"),
            "verdict": evaluation.get("verdict"),
            "detailed_feedback": evaluation.get("detailed_feedback", []),
            "oracle_reaction": evaluation.get("oracle_reaction"),
            "unlocked_lore": evaluation.get("unlocked_lore")
        },
        
        # Oracle state
        "oracle_state": {
            "tone": oracle_state["oracle_tone"],
            "emotion": oracle_state["oracle_emotion"],
            "intensity": oracle_state["intensity"],
            "next_tone": oracle_state["next_tone"],
            "atmospheric_message": oracle_state["atmospheric_message"],
            "behavior": oracle_state["oracle_behavior"],
            "narrative": oracle_state["narrative_context"]
        },
        
        # Rewards
        "rewards": rewards,
        
        # Updated player profile
        "player_profile": updated_profile,
        
        # Recommendations
        "recommendations": recommendations,
        
        # Lore
        "lore": lore_output,
        
        # Next actions - UPDATED with adaptive difficulty and theme
        "next_action": evaluation.get("next_action", "continue"),
        "next_difficulty": next_difficulty,
        "next_theme": next_theme
    }
    
    print(f"[OK] Full chain complete | Next: {response['next_action']}")
    print(f"[OK] Next Quiz: {next_difficulty} difficulty | {next_theme} theme")
    
    # Save user context after RLOM cycle
    try:
        from oracle_engine.memory import TemporaryMemory
        context_data = {
            "player_profile": updated_profile,
            "oracle_state": oracle_state,
            "quiz_history": updated_profile.get("quiz_history", []),
            "next_difficulty": next_difficulty,
            "next_theme": next_theme
        }
        TemporaryMemory.save_context(user_id, context_data)
        print(f"[OK] User context saved to disk")
    except Exception as e:
        print(f"[WARN] Failed to save context: {e}")
    
    print(f"{'='*60}\n")
    
    return response


def pick_next_difficulty_and_theme(accuracy: float, current_difficulty: str, current_theme: str, player_profile: dict) -> tuple:
    """
    Dynamically pick the next difficulty and theme based on quiz performance.
    
    Args:
        accuracy: Quiz accuracy (0.0-1.0)
        current_difficulty: Current difficulty level
        current_theme: Current theme/subgenre
        player_profile: Player's profile with stats
        
    Returns:
        tuple: (next_difficulty, next_theme)
    """
    import random
    import time
    
    # Randomize seed for variety
    random.seed(time.time())
    
    # Difficulty progression logic
    difficulty_levels = ["beginner", "intermediate", "advanced", "expert"]
    current_idx = difficulty_levels.index(current_difficulty.lower()) if current_difficulty.lower() in difficulty_levels else 1
    
    if accuracy >= 0.85:
        # Excellent performance - increase difficulty
        next_idx = min(current_idx + 1, len(difficulty_levels) - 1)
        print(f"[DIFFICULTY] Excellent performance ({accuracy*100:.0f}%) - Increasing difficulty")
    elif accuracy >= 0.60:
        # Good performance - keep same or slightly increase
        next_idx = current_idx if random.random() < 0.5 else min(current_idx + 1, len(difficulty_levels) - 1)
        print(f"[DIFFICULTY] Good performance ({accuracy*100:.0f}%) - Maintaining difficulty")
    elif accuracy >= 0.40:
        # Average performance - keep same or slightly decrease
        next_idx = current_idx if random.random() < 0.6 else max(current_idx - 1, 0)
        print(f"[DIFFICULTY] Average performance ({accuracy*100:.0f}%) - Adjusting difficulty")
    else:
        # Poor performance - decrease difficulty
        next_idx = max(current_idx - 1, 0)
        print(f"[DIFFICULTY] Poor performance ({accuracy*100:.0f}%) - Decreasing difficulty")
    
    next_difficulty = difficulty_levels[next_idx]
    
    # Theme rotation - always pick a different theme for variety
    all_themes = [
        "general_horror", "slasher", "psychological", "supernatural",
        "zombie", "vampire", "cosmic", "gothic", "body_horror",
        "found_footage", "haunted_house", "folklore", "survival"
    ]
    
    # Remove current theme from options
    available_themes = [t for t in all_themes if t != current_theme]
    
    # Bias towards preferred themes if in player profile
    preferred_themes = player_profile.get("preferred_themes", [])
    if preferred_themes and random.random() < 0.4:  # 40% chance to use preferred theme
        preferred_available = [t for t in preferred_themes if t in available_themes]
        if preferred_available:
            next_theme = random.choice(preferred_available)
            print(f"[THEME] Selected preferred theme: {next_theme}")
        else:
            next_theme = random.choice(available_themes)
            print(f"[THEME] Random theme (no preferred available): {next_theme}")
    else:
        # Random theme from available options
        next_theme = random.choice(available_themes)
        print(f"[THEME] Random theme for variety: {next_theme}")
    
    print(f"[NEXT QUIZ] Difficulty: {next_difficulty} | Theme: {next_theme}")
    
    return next_difficulty, next_theme


def demo_fear_meter_integration():
    """
    Demonstrates the Fear Meter integration with different accuracy levels.
    """
    print("=" * 60)
    print("HORROR ORACLE - FEAR METER DEMONSTRATION")
    print("=" * 60)
    
    # Sample player profile
    player = {
        "name": "DarkSeeker",
        "bravery": 65,
        "lore_knowledge": 70,
        "logic": 75,
        "fear_level": 50
    }
    
    # Test different accuracy scenarios
    scenarios = [
        (1.0, "Perfect Score"),
        (0.8, "Good Performance"),
        (0.5, "Average Performance"),
        (0.3, "Poor Performance"),
        (0.1, "Very Poor Performance")
    ]
    
    previous_tone = "neutral"
    
    for accuracy, label in scenarios:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {label} (Accuracy: {accuracy*100:.0f}%)")
        print(f"{'='*60}")
        
        fear_meter = FearMeterNode()
        result = fear_meter.translate_to_oracle_state(
            accuracy=accuracy,
            previous_tone=previous_tone,
            player_profile=player
        )
        
        print(f"\n[ORACLE STATE]")
        print(f"   Tone: {result['oracle_tone']}")
        print(f"   Emotion: {result['oracle_emotion']}")
        print(f"   Intensity: {result['intensity']:.2f}")
        print(f"   Next Tone: {result['next_tone']}")
        
        print(f"\n[PLAYER STATE]")
        print(f"   Confidence: {result['player_state']['confidence']}")
        print(f"   Fear Level: {result['player_state']['fear_level']}")
        print(f"   Trend: {result['player_state']['performance_trend']}")
        
        print(f"\n[ORACLE BEHAVIOR]")
        print(f"   Difficulty: {result['oracle_behavior']['difficulty_adjustment']}")
        print(f"   Reveal Lore: {result['oracle_behavior']['reveal_lore']}")
        print(f"   Mock Intensity: {result['oracle_behavior']['mock_intensity']}")
        print(f"   Rewards: {result['oracle_behavior']['rewards_granted']}")
        
        print(f"\n[NARRATIVE]")
        print(f"   Atmosphere: {result['narrative_context']['chamber_atmosphere']}")
        print(f"   Oracle Stance: {result['narrative_context']['oracle_stance']}")
        
        print(f"\n[ORACLE'S MESSAGE]")
        print(f"   \"{result['atmospheric_message']}\"")
        
        print(f"\n[TRANSITION]")
        print(f"   {result['narrative_context']['transition_text']}")
        
        # Update for next iteration
        previous_tone = result['next_tone']
        player['fear_level'] = result['player_state']['fear_level']
    
    print(f"\n{'='*60}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Run the demonstration
    demo_fear_meter_integration()
