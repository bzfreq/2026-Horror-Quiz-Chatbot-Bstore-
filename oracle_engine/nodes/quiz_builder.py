import random, json, os

def build_quiz(user_id):
    # Temporary example data, will later call LLM
    sample_questions = [
        {"question": "In The Shining, what weapon does Jack use?", 
         "options": ["Axe", "Bat", "Knife", "Hammer"], 
         "answer": "Axe"},
        {"question": "What's the name of the killer in Scream?", 
         "options": ["Ghostface", "Michael", "Chucky", "Jason"], 
         "answer": "Ghostface"},
        {"question": "Which film features a puzzle box that summons demons?", 
         "options": ["Hellraiser", "Saw", "The Thing", "Phantasm"], 
         "answer": "Hellraiser"},
        {"question": "Who directed Get Out?", 
         "options": ["Jordan Peele", "James Wan", "Sam Raimi", "John Carpenter"], 
         "answer": "Jordan Peele"},
        {"question": "In The Exorcist, what is the possessed girl's name?", 
         "options": ["Regan", "Linda", "Carrie", "Susan"], 
         "answer": "Regan"}
    ]
    return {"chamber_name": "The Hall of Shadows", "questions": random.sample(sample_questions, 5)}













