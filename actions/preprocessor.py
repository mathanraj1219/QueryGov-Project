import re
from textblob import TextBlob
from nltk.corpus import wordnet
from difflib import get_close_matches

# You may need to run:
# import nltk
# nltk.download('wordnet')

# Predefined concept clusters for synonym mapping
CONCEPT_SYNONYMS = {
    "cost": ["fee", "price", "charge", "amount", "payment"],
    "documents": ["papers", "proof", "ids", "requirements", "files"],
    "where": ["location", "apply", "submit", "place"],
    "authority": ["who issues", "issuer", "department", "office"],
    "lost": ["misplaced", "gone", "duplicate", "lost it"],
}

def normalize_to_concept(word):
    for concept, synonyms in CONCEPT_SYNONYMS.items():
        if word.lower() == concept or word.lower() in synonyms:
            return concept
        else:
            # Try fuzzy match
            match = get_close_matches(word.lower(), synonyms, n=1, cutoff=0.75)
            if match:
                return concept
    return word

def preprocess_user_input(text: str) -> str:
    # Step 1: Correct grammar/spelling
    corrected = str(TextBlob(text).correct())

    # Step 2: Normalize synonyms
    tokens = re.findall(r"\w+|\S", corrected)
    processed = [normalize_to_concept(token) for token in tokens]
    return " ".join(processed)

