# Fear Meter - Usage Examples

## Quick Start

```python
from oracle_engine.fear_meter_node import FearMeterNode

# Create Fear Meter instance
fear_meter = FearMeterNode()

# Define player profile
player_profile = {
    "name": "HorrorFan123",
    "bravery": 70,
    "lore_knowledge": 65,
    "logic": 80,
    "fear_level": 50
}

# Get Oracle state based on quiz performance
oracle_state = fear_meter.translate_to_oracle_state(
    accuracy=0.85,              # 85% accuracy
    previous_tone="neutral",    # Previous interaction tone
    player_profile=player_profile
)

# Access the results
print(oracle_state["atmospheric_message"])
# "The Oracle nods slowly. 'The old ways are not lost on you.'"
```

---

## Full Quiz Integration

```python
from oracle_engine.fear_meter_node import FearMeterNode

def complete_quiz_flow():
    """Complete quiz evaluation with Fear Meter integration."""
    
    # 1. Player takes quiz
    quiz = {
        "questions": [
            {"question": "What year was The Exorcist released?", 
             "answer": "1973", "user_answer": "1973"},
            {"question": "Who directed Psycho?", 
             "answer": "Alfred Hitchcock", "user_answer": "Alfred Hitchcock"},
            {"question": "What is the Babadook?", 
             "answer": "A monster", "user_answer": "Wrong"}
        ]
    }
    
    # 2. Calculate accuracy
    correct = sum(1 for q in quiz["questions"] 
                  if q["answer"] == q["user_answer"])
    accuracy = correct / len(quiz["questions"])
    # Result: 2/3 = 0.67 (67%)
    
    # 3. Get player profile (from database/session)
    player_profile = {
        "name": "Sarah",
        "bravery": 55,
        "lore_knowledge": 60,
        "logic": 70,
        "fear_level": 45
    }
    
    # 4. Translate to Oracle state
    fear_meter = FearMeterNode()
    oracle_state = fear_meter.translate_to_oracle_state(
        accuracy=accuracy,
        previous_tone="neutral",  # From last quiz
        player_profile=player_profile
    )
    
    # 5. Display results to player
    print(f"\nScore: {correct}/{len(quiz['questions'])}")
    print(f"\n{oracle_state['atmospheric_message']}")
    print(f"\n{oracle_state['narrative_context']['transition_text']}")
    
    # 6. Update player profile
    player_profile["fear_level"] = oracle_state["player_state"]["fear_level"]
    
    # 7. Apply behavioral changes
    if oracle_state["oracle_behavior"]["reveal_lore"]:
        unlock_lore_content()
    
    if oracle_state["oracle_behavior"]["difficulty_adjustment"] == "reward":
        adjust_difficulty(easier=True)
    elif oracle_state["oracle_behavior"]["difficulty_adjustment"] == "punish":
        adjust_difficulty(easier=False)
    
    # 8. Store tone for next interaction
    next_quiz_tone = oracle_state["next_tone"]
    
    return oracle_state
```

---

## Response Display Examples

### Example 1: Perfect Score (100%)
```python
accuracy = 1.0
result = fear_meter.translate_to_oracle_state(accuracy, "neutral", player)

# Result:
{
    "oracle_tone": "reverent",
    "atmospheric_message": "The Oracle's eyes gleam with approval. 'You are worthy of the deeper mysteries.'",
    "player_state": {
        "confidence": "confident",
        "fear_level": 30  # Decreased from 50
    },
    "oracle_behavior": {
        "difficulty_adjustment": "reward",
        "reveal_lore": True,
        "rewards_granted": ["lore_fragment", "oracle_blessing"]
    }
}

# Display to player:
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 PERFECT SCORE! 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The Oracle rises from its throne, robes flowing 
like shadow and light intertwined, power radiating 
from every gesture.

"The Oracle's eyes gleam with approval. You are 
worthy of the deeper mysteries."

Your mastery opens new paths... The Oracle prepares 
deeper mysteries.

✨ REWARDS UNLOCKED:
   • Lore Fragment
   • Oracle's Blessing

Fear Level: 30 (-20)
Confidence: CONFIDENT
"""
```

### Example 2: Good Performance (75%)
```python
accuracy = 0.75
result = fear_meter.translate_to_oracle_state(accuracy, "neutral", player)

# Display to player:
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ GOOD PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The Oracle sits motionless, eyes older than time 
itself watching patiently.

"You understand more than most," the Oracle intones 
solemnly.

The Oracle continues to test your resolve...

✨ REWARDS UNLOCKED:
   • Lore Fragment

Fear Level: 40 (-10)
Confidence: Confident
"""
```

### Example 3: Poor Performance (25%)
```python
accuracy = 0.25
result = fear_meter.translate_to_oracle_state(accuracy, "neutral", player)

# Display to player:
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ DISAPPOINTING...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The Oracle leans forward, eyes gleaming with dark 
amusement and malice, power radiating from every 
gesture.

"The Oracle's laughter echoes through the chamber. 
'You stumble, mortal!'"

Your failure amuses the ancient one... Prepare for 
harsher trials.

⚠ WARNING: Difficulty increased
❌ No rewards granted

Fear Level: 65 (+15)
Confidence: Terrified
"""
```

---

## Progressive Quiz Session

```python
def run_quiz_session():
    """Demonstrate how Oracle tone evolves over multiple quizzes."""
    
    fear_meter = FearMeterNode()
    
    player = {
        "name": "Player1",
        "bravery": 50,
        "lore_knowledge": 50,
        "logic": 50,
        "fear_level": 50
    }
    
    # Track tone progression
    current_tone = "neutral"
    
    # Quiz 1: Average performance
    print("=== QUIZ 1: Chamber of Initiation ===")
    result1 = fear_meter.translate_to_oracle_state(0.6, current_tone, player)
    print(f"Tone: {result1['oracle_tone']}")
    print(f"Message: {result1['atmospheric_message']}")
    
    # Update state
    current_tone = result1["next_tone"]
    player["fear_level"] = result1["player_state"]["fear_level"]
    
    # Quiz 2: Improved performance
    print("\n=== QUIZ 2: Chamber of Shadows ===")
    result2 = fear_meter.translate_to_oracle_state(0.85, current_tone, player)
    print(f"Tone: {result2['oracle_tone']}")
    print(f"Message: {result2['atmospheric_message']}")
    
    # Update state
    current_tone = result2["next_tone"]
    player["fear_level"] = result2["player_state"]["fear_level"]
    
    # Quiz 3: Perfect performance
    print("\n=== QUIZ 3: Chamber of Mastery ===")
    result3 = fear_meter.translate_to_oracle_state(1.0, current_tone, player)
    print(f"Tone: {result3['oracle_tone']}")
    print(f"Message: {result3['atmospheric_message']}")
    
    print(f"\nFinal Fear Level: {result3['player_state']['fear_level']}")
    print(f"Total Rewards: {len(result1['oracle_behavior']['rewards_granted']) + len(result2['oracle_behavior']['rewards_granted']) + len(result3['oracle_behavior']['rewards_granted'])}")

# Output shows natural progression:
# neutral → creepy → ancient → reverent
# Fear level: 50 → 50 → 40 → 20
```

---

## API Integration

### Flask/FastAPI Endpoint Example

```python
from flask import Flask, request, jsonify
from oracle_engine.fear_meter_node import FearMeterNode

app = Flask(__name__)
fear_meter = FearMeterNode()

@app.route('/api/quiz/evaluate', methods=['POST'])
def evaluate_quiz():
    """Evaluate quiz and return Oracle state."""
    
    data = request.json
    
    # Calculate accuracy
    score = data['score']
    total = data['total']
    accuracy = score / total if total > 0 else 0
    
    # Get player data
    player_profile = {
        "name": data.get('player_name', 'Unknown'),
        "bravery": data.get('bravery', 50),
        "lore_knowledge": data.get('lore_knowledge', 50),
        "logic": data.get('logic', 50),
        "fear_level": data.get('fear_level', 50)
    }
    
    previous_tone = data.get('previous_tone', 'neutral')
    
    # Get Oracle state
    oracle_state = fear_meter.translate_to_oracle_state(
        accuracy=accuracy,
        previous_tone=previous_tone,
        player_profile=player_profile
    )
    
    # Return full response
    return jsonify({
        "score": score,
        "total": total,
        "accuracy": accuracy,
        "oracle_state": oracle_state,
        "success": True
    })

# Example request:
"""
POST /api/quiz/evaluate
{
    "score": 8,
    "total": 10,
    "player_name": "HorrorFan",
    "bravery": 65,
    "lore_knowledge": 70,
    "logic": 75,
    "fear_level": 45,
    "previous_tone": "neutral"
}
"""
```

---

## Frontend JavaScript Integration

```javascript
async function submitQuiz(score, total, playerData) {
    const response = await fetch('/api/quiz/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            score: score,
            total: total,
            ...playerData
        })
    });
    
    const result = await response.json();
    const oracle = result.oracle_state;
    
    // Display Oracle response
    displayOracleMessage(oracle.atmospheric_message);
    displayOracleStance(oracle.narrative_context.oracle_stance);
    displayTransition(oracle.narrative_context.transition_text);
    
    // Update UI based on behavior
    if (oracle.oracle_behavior.reveal_lore) {
        unlockLoreSection();
    }
    
    // Update player stats
    updateFearLevel(oracle.player_state.fear_level);
    updateConfidence(oracle.player_state.confidence);
    
    // Show rewards
    oracle.oracle_behavior.rewards_granted.forEach(reward => {
        showRewardNotification(reward);
    });
    
    // Store next tone for next quiz
    localStorage.setItem('oracle_tone', oracle.next_tone);
}
```

---

## Custom Tone Messages

You can extend the atmospheric messages by modifying the `_generate_atmospheric_message()` method:

```python
# In fear_meter_node.py, add more messages to each tone:

messages = {
    "reverent": [
        "The Oracle bows slightly. 'Well done, {player_name}...'",
        "Your mastery has been noted...",
        "The ancient one acknowledges your skill...",
        # Add more variations
    ],
    # ... etc
}
```

---

## Best Practices

1. **Always store the `next_tone`** for the next quiz interaction
2. **Update player fear_level** in your database/session
3. **Apply difficulty adjustments** before generating next quiz
4. **Display atmospheric elements** to enhance immersion
5. **Track rewards** and unlock content appropriately
6. **Log Oracle interactions** for analytics and debugging

---

## Troubleshooting

**Q: Fear level not changing?**
A: Ensure you're updating `player_profile["fear_level"]` with the returned value.

**Q: Same tone every time?**
A: Make sure you're passing the `next_tone` from previous quiz as `previous_tone`.

**Q: No rewards granted?**
A: Check accuracy threshold - lore unlocks at 70%+, blessings at 90%+.

**Q: Atmospheric messages repetitive?**
A: Consider adding more message variations or integrating with LangChain for AI-generated responses.

---

For complete documentation, see `FEAR_METER_DOCUMENTATION.md`

