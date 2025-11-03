 
import os
import requests
import json
from time import sleep

# === CONFIG ===
API_KEY = "6ab7b8b2"  # Get one free at https://www.omdbapi.com/apikey.aspx
OUTPUT_DIR = "data/horror_movies"
GENRE = "horror"
MAX_MOVIES = 50

# Example seed titles (you can expand this list anytime)
MOVIES = [
    "The Exorcist", "The Shining", "Psycho", "Halloween", "The Thing", "Hereditary",
    "Get Out", "It Follows", "Evil Dead", "The Babadook", "The Conjuring", "Midsommar",
    "The Blair Witch Project", "The Texas Chain Saw Massacre", "A Nightmare on Elm Street",
    "Rosemary's Baby", "Suspiria", "The Witch", "Scream", "The Ring", "Poltergeist",
    "The Omen", "Insidious", "Hellraiser", "The Cabin in the Woods", "Candyman",
    "The Grudge", "The Others", "Pet Sematary", "28 Days Later", "The Descent",
    "The Fly", "The Mist", "Train to Busan", "The Autopsy of Jane Doe", "Sinister",
    "It", "The Nun", "The Black Phone", "Talk to Me", "Pearl", "X", "Smile",
    "The Invitation", "Don't Breathe", "The Visit", "Us", "The Invisible Man"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_movie_data(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("Response") == "True":
            return {
                "Title": data.get("Title"),
                "Year": data.get("Year"),
                "Director": data.get("Director"),
                "Plot": data.get("Plot"),
                "Genre": data.get("Genre"),
                "IMDB_Rating": data.get("imdbRating"),
            }
    except Exception as e:
        print(f"Error fetching {title}: {e}")
    return None

def save_movie_text(movie):
    filename = f"{movie['Title'].replace(' ', '_')}.txt"
    path = os.path.join(OUTPUT_DIR, filename)
    text = (
        f"Title: {movie['Title']}\n"
        f"Year: {movie['Year']}\n"
        f"Director: {movie['Director']}\n"
        f"Genre: {movie['Genre']}\n"
        f"IMDB_Rating: {movie['IMDB_Rating']}\n\n"
        f"Plot Summary:\n{movie['Plot']}\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    print(f"Fetching {len(MOVIES)} horror movies...")
    count = 0
    for title in MOVIES:
        movie = fetch_movie_data(title)
        if movie:
            save_movie_text(movie)
            count += 1
            print(f"✅ Saved: {movie['Title']}")
        else:
            print(f"⚠️ Skipped: {title}")
        sleep(0.8)  # avoid rate limiting
        if count >= MAX_MOVIES:
            break
    print(f"\n🎃 Done. {count} movies saved in '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    main()
