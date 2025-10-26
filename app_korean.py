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
    
    # Look for video files
    for ext in ['.mp4', '.avi', '.mov']:
        video_path = os.path.join(media_folder, f"{word.lower()}{ext}")
        if os.path.exists(video_path):
            st.video(video_path)
            return

def korean_study_mode():
    """Korean vocabulary study mode"""
    korean_data = load_korean_vocabulary()
    
    if not korean_data:
        st.error("Korean vocabulary file (korean.json) not found!")
        return
    
    st.header("🇰🇷 Korean Vocabulary Study")
    
    # Category selection
    categories = list(korean_data.keys())
    selected_category = st.selectbox("Choose a category:", categories)
    
    if selected_category and selected_category in korean_data:
        words = korean_data[selected_category]
        
        if words:
            # Word selection
            word_options = [f"{word['word']} ({word.get('meaning', 'No meaning')})" for word in words]
            selected_word_index = st.selectbox("Choose a word:", range(len(word_options)), 
                                             format_func=lambda x: word_options[x])
            
            if selected_word_index is not None:
                word_data = words[selected_word_index]
                
                # Display word information
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📝 Word Information")
                    st.write(f"**Korean Word:** {word_data['word']}")
                    st.write(f"**English Meaning:** {word_data.get('meaning', 'No meaning provided')}")
                    
                    # Display phrase
                    if 'phrase' in word_data:
                        st.write("**English Phrase:**")
                        st.info(word_data['phrase'])
                    
                    # Display Korean phrase if available
                    if 'korean_phrase' in word_data:
                        st.write("**Korean Phrase:**")
                        st.success(word_data['korean_phrase'])
                
                with col2:
                    # Display media content
                    display_media_content(word_data['word'])
                    
                    # Audio controls
                    st.subheader("🔊 Audio")
                    
                    # Speed selection
                    speed_key = st.selectbox("Select speech speed:", 
                                           SPEED_OPTIONS, 
                                           format_func=lambda x: SPEED_LABELS[x])
                    speed = 1.0 if speed_key == "normal" else float(speed_key)
                    
                    col_audio1, col_audio2 = st.columns(2)
                    
                    with col_audio1:
                        # Korean word audio
                        if st.button("🎵 Play Korean Word"):
                            audio_file = create_audio_file(word_data['word'], speed)
                            if audio_file and os.path.exists(audio_file):
                                with open(audio_file, 'rb') as f:
                                    st.audio(f.read(), format='audio/mp3')
                                cleanup_audio_file(audio_file)
                    
                    with col_audio2:
                        # Korean phrase audio
                        if st.button("🎵 Play Korean Phrase") and 'korean_phrase' in word_data:
                            audio_file = create_audio_file(word_data['korean_phrase'], speed)
                            if audio_file and os.path.exists(audio_file):
                                with open(audio_file, 'rb') as f:
                                    st.audio(f.read(), format='audio/mp3')
                                cleanup_audio_file(audio_file)
                
                # Display expressions
                st.subheader("💬 Expressions")
                
                if 'expressions' in word_data and word_data['expressions']:
                    col_expr1, col_expr2 = st.columns(2)
                    
                    with col_expr1:
                        st.write("**English Expressions:**")
                        for expr in word_data['expressions']:
                            st.write(f"• {expr}")
                    
                    with col_expr2:
                        if 'korean_expressions' in word_data and word_data['korean_expressions']:
                            st.write("**Korean Expressions:**")
                            for expr in word_data['korean_expressions']:
                                st.write(f"• {expr}")

def korean_quiz_mode():
    """Korean vocabulary quiz mode"""
    korean_data = load_korean_vocabulary()
    
    if not korean_data:
        st.error("Korean vocabulary file (korean.json) not found!")
        return
    
    st.header("🧠 Korean Vocabulary Quiz")
    
    # Category selection for quiz
    categories = list(korean_data.keys())
    selected_category = st.selectbox("Choose quiz category:", categories, key="quiz_category")
    
    if selected_category and selected_category in korean_data:
        words = korean_data[selected_category]
        
        if len(words) < 4:
            st.warning("Need at least 4 words in category for quiz mode.")
            return
        
        if st.button("🎯 Start New Quiz"):
            # Initialize quiz session
            quiz_word = random.choice(words)
            other_words = [w for w in words if w['word'] != quiz_word['word']]
            wrong_answers = random.sample(other_words, min(3, len(other_words)))
            
            # Store in session state
            st.session_state.quiz_word = quiz_word
            st.session_state.quiz_options = [quiz_word] + wrong_answers
            random.shuffle(st.session_state.quiz_options)
            st.session_state.quiz_answered = False
            st.session_state.quiz_score = getattr(st.session_state, 'quiz_score', 0)
            st.session_state.quiz_total = getattr(st.session_state, 'quiz_total', 0)
        
        # Display quiz if active
        if hasattr(st.session_state, 'quiz_word') and not st.session_state.get('quiz_answered', False):
            quiz_word = st.session_state.quiz_word
            
            st.subheader("Question:")
            st.write(f"**English Meaning:** {quiz_word['meaning']}")
            
            if 'phrase' in quiz_word:
                st.write(f"**Example Phrase:** {quiz_word['phrase']}")
            
            st.write("**What is the Korean word?**")
            
            # Quiz options
            for i, option in enumerate(st.session_state.quiz_options):
                if st.button(f"{chr(65+i)}. {option['word']}", key=f"option_{i}"):
                    st.session_state.quiz_total += 1
                    
                    if option['word'] == quiz_word['word']:
                        st.session_state.quiz_score += 1
                        st.success(f"✅ Correct! The answer is: {quiz_word['word']}")
                        
                        # Play audio for correct answer
                        audio_file = create_audio_file(quiz_word['word'], 1.0)
                        if audio_file and os.path.exists(audio_file):
                            with open(audio_file, 'rb') as f:
                                st.audio(f.read(), format='audio/mp3')
                            cleanup_audio_file(audio_file)
                    else:
                        st.error(f"❌ Wrong! The correct answer is: {quiz_word['word']}")
                    
                    st.session_state.quiz_answered = True
                    
                    # Show score
                    accuracy = (st.session_state.quiz_score / st.session_state.quiz_total) * 100
                    st.info(f"Score: {st.session_state.quiz_score}/{st.session_state.quiz_total} ({accuracy:.1f}%)")
        
        elif hasattr(st.session_state, 'quiz_score'):
            # Show current score
            accuracy = (st.session_state.quiz_score / max(st.session_state.quiz_total, 1)) * 100
            st.info(f"Current Score: {st.session_state.quiz_score}/{st.session_state.quiz_total} ({accuracy:.1f}%)")

def main():
    st.set_page_config(
        page_title="Korean Vocabulary Builder",
        page_icon="🇰🇷",
        layout="wide"
    )
    
    st.title("🇰🇷 Korean Vocabulary Builder")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    mode = st.sidebar.radio(
        "Select Mode:",
        ["Study Mode", "Quiz Mode"]
    )
    
    # Main content based on selected mode
    if mode == "Study Mode":
        korean_study_mode()
    elif mode == "Quiz Mode":
        korean_quiz_mode()
    
    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Korean Learning Tips")
    st.sidebar.markdown("""
    - Listen to pronunciation carefully
    - Practice writing Korean characters
    - Use phrases in context
    - Review expressions regularly
    - Take quizzes to test knowledge
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Categories Available")
    korean_data = load_korean_vocabulary()
    if korean_data:
        for category, words in korean_data.items():
            st.sidebar.markdown(f"- **{category.title()}**: {len(words)} words")

if __name__ == "__main__":
    main()