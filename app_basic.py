import streamlit as st 
import os
from main import (
    load_word_pools, 
    create_audio_file, 
    load_vocabulary_from_file, 
    save_word_pools_to_file,
    filter_words_by_category,
    validate_word_entry,
    cleanup_audio_file,
    DEFAULT_CATEGORIES,
    DEFAULT_VOCABULARY_FILE,
    DIFFICULTY_LEVELS,
    LEVEL_DESCRIPTIONS,
    SPEED_OPTIONS,
    SPEED_LABELS
) 

def update_phrase_in_file(word_to_update, new_phrase, word_file):
    """Update the phrase for a specific word in the vocabulary file"""
    # Read all lines
    with open(word_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update the specific word's phrase
    updated_lines = []
    updated = False
    for line in lines:
        if line.strip():
            parts = line.strip().split(' | ')
            if len(parts) >= 4 and parts[0].lower() == word_to_update.lower():
                # Update the phrase (index 2)
                parts[2] = new_phrase
                updated_lines.append(' | '.join(parts) + '\n')
                updated = True
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Write back to file
    if updated:
        with open(word_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
    
    return updated

st.title("My Vocabulary Builder")

st.header("Welcome to My Vocabulary Builder!")
st.subheader("Enhance your vocabulary with ease")

# Level Selection in main area
st.markdown("### 🎯 Select Your Learning Level")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📚 **Level 1: Beginner**\n\nBasic vocabulary with common everyday words", key="level1"):
        st.session_state.selected_level = 1

with col2:
    if st.button("📖 **Level 2: Intermediate**\n\nMore challenging words for advancing learners", key="level2"):
        st.session_state.selected_level = 2

with col3:
    if st.button("🎓 **Level 3: Advanced**\n\nSophisticated vocabulary for expert learners", key="level3"):
        st.session_state.selected_level = 3

# Initialize session state
if 'selected_level' not in st.session_state:
    st.session_state.selected_level = 1

# Display current level
current_level = st.session_state.selected_level
st.info(f"🎯 **Current Level: {current_level}** - {LEVEL_DESCRIPTIONS[current_level]}")

st.sidebar.title("Navigation")

# Configuration
word_file = DEFAULT_VOCABULARY_FILE
category_list = DEFAULT_CATEGORIES
word_list = []

st.write("Use the sidebar to navigate through different sections.")

# Add a button to load predefined word pools for selected level
if st.button(f"📚 Load Level {current_level} Vocabulary (160 words)", help=f"Load 20 words for each category at Level {current_level}"):
    word_pools = load_word_pools(current_level)
    if word_pools:
        success = save_word_pools_to_file(word_pools, word_file)
        if success:
            st.success(f"✅ Successfully loaded Level {current_level} vocabulary with 160 words across all categories!")
            st.info("Navigate to 'View Words' to see the loaded vocabulary.")
        else:
            st.error("❌ Error loading sample vocabulary.")
    else:
        st.error(f"❌ Could not load Level {current_level} word pools from JSON file.")

select = st.sidebar.radio("Select Your action", ["Add Word", "View Words"])
if select == "Add Word":
    st.write("Add a new word to your vocabulary list.")
    word = st.text_input("Enter the word:")
    meaning = st.text_area("Enter the meaning:")
    phrase = st.text_input("Enter an example phrase):")
    category = st.radio("Select Category", category_list, horizontal=True)
    category = category.lower()
    
    if st.button("Add Word"):
        # Validate input using the main.py function
        is_valid, error_msg = validate_word_entry(word, meaning, phrase, category)
        
        if is_valid:
            st.success(f"Word '{word}' added successfully!")
            if phrase:
                # Append to file
                with open(word_file, "a", encoding='utf-8') as f:
                    f.write(f"{word} | {meaning} | {phrase} | {category}\n")
        else:
            st.error(error_msg)
            
elif select == "View Words":
    selected_category = st.sidebar.radio("Select a Category", category_list, horizontal=True)
    
    # Add speed selection in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("🔊 **Voice Speed Settings**")
    selected_speed = st.sidebar.radio(
        "Select Pronunciation Speed:",
        options=SPEED_OPTIONS,
        format_func=lambda x: SPEED_LABELS[x],
        help="Choose speed for pronunciation practice"
    )
    
    st.subheader(f"Here are the words in your vocabulary list for {selected_category}:")
    
    if selected_category:
        # Load words from file using main.py function
        all_words = load_vocabulary_from_file(word_file)
        
        # Filter words by category using main.py function
        filtered_words = filter_words_by_category(all_words, selected_category)
        
        if filtered_words:
            for entry in filtered_words:
                with st.container():
                    # Create columns for word and play buttons
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(
                            f"""
                            <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
                                <h4 style="color: #4CAF50; margin-bottom: 10px;">📚 {entry['word']}</h4>
                                <p style="font-size: 1.3em;"><strong>Meaning:</strong> {entry['meaning']}</p>
                                <p style="font-size: 1.3em;"><strong>Example Phrase:</strong> {entry['phrase']}</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        # Display media if exists (image or video)
                        media_path = entry.get('media')
                        if media_path and os.path.exists(media_path):
                            file_extension = os.path.splitext(media_path)[1].lower()
                            
                            if file_extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                                st.markdown("**🎥 Video Reference:**")
                                try:
                                    st.video(media_path)
                                except Exception as e:
                                    st.error(f"Error loading video: {str(e)}")
                            elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                                st.markdown("**📷 Visual Reference:**")
                                try:
                                    st.image(media_path, caption=f"Visual for: {entry['phrase']}", use_column_width=True)
                                except Exception as e:
                                    st.error(f"Error loading image: {str(e)}")
                            else:
                                st.warning(f"Unsupported media format: {file_extension}")
                        
                        # Change Phrase button
                        if st.button(f"✏️ Change Phrase", key=f"edit_{entry['word']}"):
                            st.session_state[f"editing_phrase_{entry['word']}"] = True
                            st.session_state[f"new_phrase_{entry['word']}"] = entry['phrase']
                        
                        # Phrase editor popup
                        if st.session_state.get(f"editing_phrase_{entry['word']}", False):
                            st.markdown("---")
                            st.markdown(f"**✏️ Edit phrase for '{entry['word']}':**")
                            
                            new_phrase = st.text_area(
                                "New phrase:",
                                value=st.session_state.get(f"new_phrase_{entry['word']}", entry['phrase']),
                                key=f"phrase_editor_{entry['word']}",
                                height=100
                            )
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                if st.button("💾 Save", key=f"save_{entry['word']}"):
                                    if new_phrase.strip():
                                        success = update_phrase_in_file(entry['word'], new_phrase.strip(), word_file)
                                        if success:
                                            st.success(f"✅ Phrase updated for '{entry['word']}'!")
                                            # Clear editing state
                                            st.session_state[f"editing_phrase_{entry['word']}"] = False
                                            if f"new_phrase_{entry['word']}" in st.session_state:
                                                del st.session_state[f"new_phrase_{entry['word']}"]
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to update phrase")
                                    else:
                                        st.error("❌ Phrase cannot be empty")
                            
                            with col_cancel:
                                if st.button("❌ Cancel", key=f"cancel_{entry['word']}"):
                                    # Clear editing state
                                    st.session_state[f"editing_phrase_{entry['word']}"] = False
                                    if f"new_phrase_{entry['word']}" in st.session_state:
                                        del st.session_state[f"new_phrase_{entry['word']}"]
                                    st.rerun()
                    
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
                        
                        # Play button for the word
                        if st.button(f"🔊 Word", key=f"word_{entry['word']}"):
                            audio_file = create_audio_file(entry['word'], f"word_{entry['word']}", is_phrase=False, speed=selected_speed)
                            if audio_file and os.path.exists(audio_file):
                                with open(audio_file, 'rb') as audio:
                                    st.audio(audio.read(), format='audio/wav')
                                cleanup_audio_file(audio_file)
                            else:
                                st.error("Audio generation failed")
                        
                        # Play button for the phrase
                        if entry['phrase'] and st.button(f"🔊 Phrase", key=f"phrase_{entry['word']}"):
                            audio_file = create_audio_file(entry['phrase'], f"phrase_{entry['word']}", is_phrase=True, speed=selected_speed)
                            if audio_file and os.path.exists(audio_file):
                                with open(audio_file, 'rb') as audio:
                                    st.audio(audio.read(), format='audio/wav')
                                cleanup_audio_file(audio_file)
                            else:
                                st.error("Audio generation failed")
        else:
            st.info("No words added yet for this category. Go to 'Add Word' to start building your vocabulary.")
    else:
        st.info("Please select a category to view words.")