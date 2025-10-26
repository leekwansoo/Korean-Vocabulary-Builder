import streamlit as st 
import json
import os
import random
from main import (
    create_audio_file, 
    cleanup_audio_file,
    SPEED_OPTIONS,
    SPEED_LABELS
)

def load_korean_vocabulary():
    """Load vocabulary from korean.json file"""
    korean_file = 'data/korean.json'
    if os.path.exists(korean_file):
        with open(korean_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_level1_categories():
    """Get beginner-friendly categories"""
    return ['general', 'health']

def display_media_content(word):
    """Display image/video if available for the word"""
    media_folder = 'media'
    if not os.path.exists(media_folder):
        return
    
    # Look for image files
    for ext in ['.jpg', '.jpeg', '.png', '.gif']:
        image_path = os.path.join(media_folder, f"{word.lower()}{ext}")
        if os.path.exists(image_path):
            st.image(image_path, caption=f"Image for: {word}", use_column_width=True)
            return

def main():
    st.set_page_config(
        page_title="Korean Level 1: Beginner",
        page_icon="🇰🇷",
        layout="wide"
    )
    
    st.title("🇰🇷 Korean Level 1: Beginner")
    st.markdown("*Perfect for starting your Korean learning journey*")
    
    korean_data = load_korean_vocabulary()
    
    if not korean_data:
        st.error("Korean vocabulary file (korean.json) not found!")
        return
    
    # Level 1 categories (beginner friendly)
    level1_categories = get_level1_categories()
    
    st.header("📚 Beginner Categories")
    selected_category = st.selectbox("Choose a category:", level1_categories)
    
    if selected_category and selected_category in korean_data:
        words = korean_data[selected_category]
        
        # Limit to first 10 words for beginners
        words = words[:10]
        
        if words:
            st.subheader(f"Learning: {selected_category.title()}")
            
            # Simple word display for beginners
            for idx, word_data in enumerate(words, 1):
                with st.expander(f"{idx}. {word_data['word']} - {word_data.get('meaning', 'No meaning')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Korean:** {word_data['word']}")
                        st.write(f"**English:** {word_data.get('meaning', 'No meaning')}")
                        
                        # Simple phrase
                        if 'korean_phrase' in word_data:
                            st.write("**Korean Phrase:**")
                            st.success(word_data['korean_phrase'])
                        
                        if 'phrase' in word_data:
                            st.write("**English Phrase:**")
                            st.info(word_data['phrase'])
                    
                    with col2:
                        display_media_content(word_data['word'])
                        
                        # Simple audio button
                        if st.button(f"🔊 Listen", key=f"audio_{idx}"):
                            audio_file = create_audio_file(word_data['word'], 0.8)  # Slower for beginners
                            if audio_file and os.path.exists(audio_file):
                                with open(audio_file, 'rb') as f:
                                    st.audio(f.read(), format='audio/mp3')
                                cleanup_audio_file(audio_file)
                        # Play Korean Phrase audio
                        if 'korean_phrase' in word_data:
                            if st.button(f"🔊 Play Korean Phrase", key=f"korean_phrase_audio_{idx}"):
                                audio_file = create_audio_file(word_data['korean_phrase'], 0.8)
                                if audio_file and os.path.exists(audio_file):
                                    with open(audio_file, 'rb') as f:
                                        st.audio(f.read(), format='audio/mp3')
                                    cleanup_audio_file(audio_file)
    
    # Sidebar with beginner tips
    st.sidebar.title("🌟 Beginner Tips")
    st.sidebar.markdown("""
    ### Level 1 Learning Guide:
    - Start with basic words
    - Listen to pronunciation
    - Practice daily
    - Don't rush - take your time
    - Focus on common words first
    
    ### What you'll learn:
    - Essential Korean words
    - Basic pronunciation
    - Simple phrases
    - Everyday vocabulary
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Your Progress")
    st.sidebar.markdown(f"**Categories**: {len(level1_categories)}")
    if korean_data:
        total_words = sum(len(korean_data.get(cat, [])[:10]) for cat in level1_categories if cat in korean_data)
        st.sidebar.markdown(f"**Total Words**: {total_words}")

if __name__ == "__main__":
    main()