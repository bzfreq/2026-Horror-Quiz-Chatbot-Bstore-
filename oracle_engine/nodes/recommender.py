import random

def recommend_next(user, score):
    chambers = [
        "Chamber of Blood", "Crypt of Whispers", 
        "Labyrinth of Screams", "Hall of Forgotten Souls", 
        "The Oracle's Trial"
    ]
    return {"next_chamber": random.choice(chambers), "difficulty": "medium"}













