"""
Evaluator Node (Answer Evaluator)
Evaluates user answers and provides feedback using LangChain and prompt templates.
"""
import json
from typing import Dict, List, Optional

# Try to import LangChain dependencies (optional)
try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.output_parsers import JsonOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatOpenAI = None
    ChatPromptTemplate = None
    JsonOutputParser = None

from oracle_engine.prompt_loader import load_prompt
from backend.config import Config


class EvaluatorNode:
    """
    Evaluates user quiz answers and generates atmospheric Oracle feedback.
    Uses LangChain and the Horror Oracle's Judgment Engine prompt.
    """
    
    def __init__(self):
        """Initialize the Evaluator node with LangChain components."""
        self.prompt_template = None
        self.reactor_prompt = None
        self.llm = None
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """Initialize LangChain LLM for feedback generation."""
        try:
            Config.validate()
            if Config.OPENAI_API_KEY:
                self.llm = ChatOpenAI(
                    model=Config.LLM_MODEL,
                    temperature=0.9,  # High temperature for creative, atmospheric feedback
                    openai_api_key=Config.OPENAI_API_KEY
                )
                print("[OK] Evaluator Node: LLM initialized")
            else:
                print("[WARN] Evaluator Node: No OpenAI API key found")
        except Exception as e:
            print(f"[WARN] Evaluator Node initialization warning: {e}")
    
    def load_prompt(self) -> str:
        """Load the answer evaluator prompt template."""
        self.prompt_template = load_prompt("answer_evaluator_prompt")
        return self.prompt_template
    
    def load_reactor_prompt(self) -> str:
        """Load the Oracle reactor prompt template."""
        self.reactor_prompt = load_prompt("oracle_reactor_prompt")
        return self.reactor_prompt
    
    def evaluate_answers(
        self,
        questions: List[Dict],
        player_answers: Dict[str, str],
        tone: str = "creepy"
    ) -> Dict:
        """
        Evaluate player's quiz answers and generate Oracle feedback.
        
        Args:
            questions: List of question dictionaries from the quiz
            player_answers: Dictionary mapping {question: player_choice}
            tone: Atmospheric tone for feedback (creepy, mocking, ancient, etc.)
            
        Returns:
            Dictionary containing:
                - score: Number of correct answers
                - total: Total number of questions
                - percentage: Score percentage
                - grade: Letter grade (S, A, B, C, D, F)
                - verdict: One-line Oracle judgment
                - detailed_feedback: Per-question feedback
                - oracle_reaction: Atmospheric reaction text
                - next_action: Recommended next step
                - unlocked_lore: Special lore if perfect score
        """
        # Calculate score first
        score = 0
        total = len(questions)
        correct_answers = {}
        
        for q in questions:
            question_text = q["question"]
            correct_answer = q["correct_answer"]
            correct_answers[question_text] = correct_answer
            
            if player_answers.get(question_text) == correct_answer:
                score += 1
        
        # Generate feedback with LLM or use fallback
        if self.llm:
            return self._generate_llm_feedback(
                questions, player_answers, correct_answers, score, total, tone
            )
        else:
            return self._fallback_feedback(
                questions, player_answers, correct_answers, score, total, tone
            )
    
    def _generate_llm_feedback(
        self,
        questions: List[Dict],
        player_answers: Dict[str, str],
        correct_answers: Dict[str, str],
        score: int,
        total: int,
        tone: str
    ) -> Dict:
        """Generate feedback using LangChain and the evaluator prompt."""
        try:
            # Load prompt if not already loaded
            if not self.prompt_template:
                self.load_prompt()
            
            # Format the prompt
            formatted_prompt = self.prompt_template.format(
                tone=tone,
                score=score,
                total=total
            )
            
            # Create chat prompt
            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are the Horror Oracle's Judgment Engine. Return ONLY valid JSON."),
                ("user", formatted_prompt + f"\n\nQuestions: {json.dumps(questions)}\n\nPlayer Answers: {json.dumps(player_answers)}\n\nCorrect Answers: {json.dumps(correct_answers)}")
            ])
            
            # Create and invoke chain
            parser = JsonOutputParser()
            chain = chat_prompt | self.llm | parser
            
            result = chain.invoke({
                "tone": tone,
                "score": score,
                "total": total,
                "questions": questions,
                "player_answers": player_answers,
                "correct_answers": correct_answers
            })
            
            # Validate and return result
            if isinstance(result, dict) and "score" in result and "oracle_reaction" in result:
                print(f"[OK] Generated Oracle feedback | Score: {score}/{total} | Tone: {tone}")
                return result
            else:
                print(f"[WARN] Unexpected feedback format, using fallback")
                return self._fallback_feedback(
                    questions, player_answers, correct_answers, score, total, tone
                )
        
        except Exception as e:
            print(f"[ERROR] Error generating feedback: {e}")
            return self._fallback_feedback(
                questions, player_answers, correct_answers, score, total, tone
            )
    
    def _fallback_feedback(
        self,
        questions: List[Dict],
        player_answers: Dict[str, str],
        correct_answers: Dict[str, str],
        score: int,
        total: int,
        tone: str
    ) -> Dict:
        """Fallback feedback when LLM is unavailable."""
        percentage = (score / total * 100) if total > 0 else 0
        
        # Calculate grade
        if percentage == 100:
            grade = "S"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 60:
            grade = "B"
        elif percentage >= 40:
            grade = "C"
        elif percentage >= 20:
            grade = "D"
        else:
            grade = "F"
        
        # Generate verdict based on tone
        verdicts = {
            "creepy": f"Your answers echo through empty corridors... {score} doors opened.",
            "mocking": f"How... quaint. You stumbled through {score} correct answers.",
            "ancient": f"Thy knowledge hath been weighed: {score} truths revealed.",
            "whispered": f"Shh... you got {score} right... don't tell the others...",
            "grim": f"Your score: {score}/{total}. The trial shows no mercy.",
            "playful": f"Ooh, {score} out of {total}! Let's see what prizes you've won..."
        }
        verdict = verdicts.get(tone, f"Score: {score}/{total}")
        
        # Generate detailed feedback
        detailed_feedback = []
        for q in questions:
            question_text = q["question"]
            player_choice = player_answers.get(question_text, "No answer")
            correct_choice = correct_answers[question_text]
            is_correct = player_choice == correct_choice
            
            comment = "Correct." if is_correct else f"Wrong. The answer was: {correct_choice}"
            
            detailed_feedback.append({
                "question": question_text,
                "player_answer": player_choice,
                "correct_answer": correct_choice,
                "is_correct": is_correct,
                "comment": comment
            })
        
        # Generate Oracle reaction
        oracle_reactions = {
            "creepy": self._creepy_reaction(score, total, percentage),
            "mocking": self._mocking_reaction(score, total, percentage),
            "ancient": self._ancient_reaction(score, total, percentage),
            "whispered": self._whispered_reaction(score, total, percentage),
            "grim": self._grim_reaction(score, total, percentage),
            "playful": self._playful_reaction(score, total, percentage)
        }
        oracle_reaction = oracle_reactions.get(tone, self._default_reaction(score, total, percentage))
        
        # Determine next action
        if percentage >= 80:
            next_action = "advance"
        elif percentage >= 60:
            next_action = "stay"
        elif percentage >= 40:
            next_action = "retry"
        else:
            next_action = "descend"
        
        # Unlocked lore for perfect score
        unlocked_lore = None
        if score == total:
            unlocked_lore = "Perfect knowledge unlocks the void's secrets. The Oracle nods in acknowledgment of a true horror scholar."
        
        return {
            "score": score,
            "total": total,
            "percentage": round(percentage, 1),
            "grade": grade,
            "verdict": verdict,
            "detailed_feedback": detailed_feedback,
            "oracle_reaction": oracle_reaction,
            "next_action": next_action,
            "unlocked_lore": unlocked_lore
        }
    
    def _creepy_reaction(self, score: int, total: int, percentage: float) -> str:
        """Generate creepy-toned reaction."""
        wrong = total - score
        if percentage == 100:
            return f"The Oracle's gaze lingers on you. Every answer... perfect. The shadows whisper your name now. You belong here, in the darkness. {score} questions, {score} truths. No light escapes."
        elif percentage >= 70:
            return f"Cold fingers trace your spine. You felt the correct answers, didn't you? {score} emerged from the void. But {wrong} remain... buried. Can you hear them screaming?"
        else:
            return f"Something moves in the corner of your vision. {score} answers clawed their way to light. {wrong} are still trapped in there... with you. The walls are listening, and they remember everything."
    
    def _mocking_reaction(self, score: int, total: int, percentage: float) -> str:
        """Generate mocking-toned reaction."""
        if percentage == 100:
            return f"Well, well. Color me impressed. {score} correct. Every. Single. One. Perhaps you're not as dull as you appeared. The Oracle grants you passage... this time."
        elif percentage >= 70:
            return f"The Oracle chuckles from the void. {score} out of {total}. Should I slow down for you? The Masters of Horror would be... mildly disappointed."
        else:
            return f"Oh dear. Oh my. {score} correct? Did you even watch these films, or just read the back of the DVD case? Pathetic. Come back when you've done your homework."
    
    def _ancient_reaction(self, score: int, total: int, percentage: float) -> str:
        """Generate ancient-toned reaction."""
        if percentage == 100:
            return f"From the depths of aeons past, the Oracle speaketh: PERFECTION. {score} answers rendered unto truth. Thou art worthy of the ancient knowledge. The elders bow before thee."
        elif percentage >= 70:
            return f"Thy knowledge hath been measured: {score} truths revealed of {total} trials. The ancient ones nod in recognition. Yet {total - score} remain shrouded in shadow's embrace."
        else:
            return f"The scales of eternity weigh thy wisdom and find it wanting. {score} answers correct, {total - score} lost to ignorance. The ancients turn their faces away."
    
    def _whispered_reaction(self, score: int, total: int, percentage: float) -> str:
        """Generate whispered-toned reaction."""
        if percentage == 100:
            return f"The Oracle leans close, breath cold against your ear. Perfect... {score} out of {score}... You know things you shouldn't. Where did you learn these secrets? Who told you?"
        elif percentage >= 70:
            return f"Listen... closer... {score} correct. Not bad. Not great. The questions you missed? They were tests within tests. But we'll keep that between us."
        else:
            return f"Shh... don't be embarrassed about the {total - score} you missed. Everyone fails sometimes. {score} right means you tried. That's... something. Isn't it?"
    
    def _grim_reaction(self, score: int, total: int, percentage: float) -> str:
        """Generate grim-toned reaction."""
        if percentage == 100:
            return f"Perfect execution. {score} correct answers. {total - score} failures. Zero margin for error. The darkness acknowledges your mastery."
        elif percentage >= 70:
            return f"The Oracle delivers judgment: {score} correct. {total - score} failures. There is no consolation in horror. You performed adequately. Nothing more."
        else:
            return f"Insufficient. {score} correct answers out of {total}. {total - score} failures. There are no participation trophies in the darkness. You either know or you don't."
    
    def _playful_reaction(self, score: int, total: int, percentage: float) -> str:
        """Generate playful-toned reaction."""
        if percentage == 100:
            return f"The Oracle claps with glee! Perfect! PERFECT! {score} out of {score}! You magnificent creature! Every answer a bullseye! You've won the grand prize: my RESPECT. Rare indeed!"
        elif percentage >= 70:
            return f"Ooh, {score} correct! Delicious! You got some wrong though... tsk tsk. But that's what makes it FUN! Every wrong answer is a little death. You're playing well, little mortal!"
        else:
            return f"The Oracle giggles maniacally! {score} right, {total - score} wrong! What a delightful disaster! You're drowning but still fighting! I LOVE it! Want to try again?"
    
    def _default_reaction(self, score: int, total: int, percentage: float) -> str:
        """Default reaction when tone is unrecognized."""
        if percentage == 100:
            return f"Perfect score: {score}/{total}. The Oracle acknowledges your mastery."
        elif percentage >= 70:
            return f"Strong performance: {score}/{total}. The Oracle watches with interest."
        else:
            return f"Score: {score}/{total}. There is room for improvement."
    
    def generate_oracle_reaction(self, score: int, total: int, context: dict) -> str:
        """
        Generate atmospheric Oracle reaction based on performance.
        
        Args:
            score: User's score
            total: Total possible score
            context: Additional context (difficulty, theme, tone, etc.)
            
        Returns:
            Oracle's reaction text
        """
        tone = context.get("tone", "creepy")
        percentage = (score / total * 100) if total > 0 else 0
        
        reactions = {
            "creepy": self._creepy_reaction,
            "mocking": self._mocking_reaction,
            "ancient": self._ancient_reaction,
            "whispered": self._whispered_reaction,
            "grim": self._grim_reaction,
            "playful": self._playful_reaction
        }
        
        reaction_func = reactions.get(tone, self._default_reaction)
        return reaction_func(score, total, percentage)


def create_evaluator_node():
    """Factory function to create an evaluator node."""
    return EvaluatorNode()

