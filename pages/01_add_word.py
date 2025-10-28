import streamlit as st 
import os
import random
from utils.validation import validate_word_entry
DEFAULT_CATEGORIES = ["general", "science", "business", "literature", "travel", "history", "geography", "health"]
DEFAULT_VOCABULARY_FILE = "vocabulary.txt"
DEFAULT_WORD_POOLS_FILE = "word_pools.json"
DIFFICULTY_LEVELS = [1, 2, 3, 4]
LEVEL_DESCRIPTIONS = {
    1: "Beginner - Basic vocabulary with common everyday words",
    2: "Intermediate - More challenging words for advancing learners", 
    3: "Advanced - Sophisticated vocabulary for expert learners",
    4: "Korean - Vocabulary for Korean language learners"
}
SPEED_OPTIONS = ["normal", "0.9", "0.8"]
SPEED_LABELS = {
    "normal": "Normal Speed",
    "0.9": "Slightly Slower (0.9x)",
    "0.8": "Slower (0.8x)"
}
st.title("Vocabulary Builder - Add New Word")
st.subheader("➕ Add New Word with Enhanced Features")

word_file = DEFAULT_VOCABULARY_FILE
category_list = DEFAULT_CATEGORIES
    
col1, col2 = st.columns(2)
with col1:
    word = st.text_input("Enter the word:")
    meaning = st.text_area("Enter the meaning:")
with col2:
    phrase = st.text_input("Enter an example phrase:")
    category = st.radio("Select Category", category_list, horizontal=True)
    # phonetic_input = st.text_input("Phonetic transcription (optional):", placeholder="e.g., /ˈɛksəmpl/")
    difficulty_level = st.radio("Difficulty Level", ["⭐ Easy", "⭐⭐ Medium", "⭐⭐⭐ Hard"], horizontal=True)

if st.button("➕ Add Word"):
    is_valid, error_msg = validate_word_entry(word, meaning, phrase, category.lower())
    
    if is_valid:
        st.success(f"Word '{word}' added successfully!")
        # Note: In a full implementation, you'd also save the phonetic and difficulty data
        with open(word_file, "a", encoding='utf-8') as f:
            f.write(f"{word} | {meaning} | {phrase} | {category.lower()}\n")
    else:
        st.error(error_msg)
