import streamlit as st 
import os
import random
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

def update_phrase_in_json(word_to_update, new_phrase, level):
    """Update the phrase for a specific word in the JSON level files"""
    import json
    
    if level == "learned":
        return update_phrase_in_learned_json(word_to_update, new_phrase)
    
    # Map level to filename
    level_files = {
        1: "data/level1.json",
        2: "data/level2.json", 
        3: "data/level3.json",
        4: "data/korean.json"
    }
    
    filename = level_files.get(level)
    if not filename or not os.path.exists(filename):
        return False
    
    try:
        # Read the JSON file
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find and update the word's phrase
        updated = False
        for category, words in data.items():
            for word_entry in words:
                if word_entry.get('word', '').lower() == word_to_update.lower():
                    word_entry['phrase'] = new_phrase
                    updated = True
                    break
            if updated:
                break
        
        # Write back to file if updated
        if updated:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        return updated
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        return False

def update_phrase_in_learned_json(word_to_update, new_phrase):
    """Update the phrase for a specific word in the learned.json file"""
    import json
    
    learned_file = "learned.json"
    if not os.path.exists(learned_file):
        return False
    
    try:
        # Read the learned.json file
        with open(learned_file, 'r', encoding='utf-8') as f:
            learned_words = json.load(f)
        
        # Find and update the word's phrase
        updated = False
        for word_entry in learned_words:
            if word_entry.get('word', '').lower() == word_to_update.lower():
                word_entry['phrase'] = new_phrase
                updated = True
                break
        
        # Write back to file if updated
        if updated:
            with open(learned_file, 'w', encoding='utf-8') as f:
                json.dump(learned_words, f, ensure_ascii=False, indent=2)
        
        return updated
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        return False

# Phonetic transcriptions for vocabulary words
PHONETICS = {
    # General
    "serendipity": "/ˌsɛrənˈdɪpɪti/",
    "eloquent": "/ˈɛləkwənt/",
    "resilient": "/rɪˈzɪliənt/",
    "pragmatic": "/prægˈmætɪk/",
    "ubiquitous": "/juˈbɪkwɪtəs/",
    "meticulous": "/məˈtɪkjələs/",
    "ephemeral": "/ɪˈfɛmərəl/",
    "versatile": "/ˈvɜrsətaɪl/",
    "ambiguous": "/æmˈbɪgjuəs/",
    "innovative": "/ˈɪnəˌveɪtɪv/",
    "tenacious": "/təˈneɪʃəs/",
    "profound": "/prəˈfaʊnd/",
    "subtle": "/ˈsʌtəl/",
    "coherent": "/koʊˈhɪrənt/",
    "diligent": "/ˈdɪlɪdʒənt/",
    "intricate": "/ˈɪntrɪkət/",
    "benevolent": "/bəˈnɛvələnt/",
    "authentic": "/ɔˈθɛntɪk/",
    "efficient": "/ɪˈfɪʃənt/",
    "contemplative": "/kənˈtɛmplətɪv/",
    
    # Science
    "hypothesis": "/haɪˈpɑθəsɪs/",
    "catalyst": "/ˈkætəlɪst/",
    "molecule": "/ˈmɑləˌkjul/",
    "ecosystem": "/ˈikoʊˌsɪstəm/",
    "photosynthesis": "/ˌfoʊtoʊˈsɪnθəsɪs/",
    "chromosome": "/ˈkroʊməˌsoʊm/",
    "quantum": "/ˈkwɑntəm/",
    "biodiversity": "/ˌbaɪoʊdaɪˈvɜrsəti/",
    "metabolism": "/məˈtæbəˌlɪzəm/",
    "neuron": "/ˈnʊrɑn/",
    "osmosis": "/ɑzˈmoʊsɪs/",
    "mitosis": "/maɪˈtoʊsɪs/",
    "genome": "/ˈdʒinoʊm/",
    "thermodynamics": "/ˌθɜrmoʊdaɪˈnæmɪks/",
    "evolution": "/ˌɛvəˈluʃən/",
    "isotope": "/ˈaɪsəˌtoʊp/",
    "enzyme": "/ˈɛnzaɪm/",
    "gravity": "/ˈgrævəti/",
    "radiation": "/ˌreɪdiˈeɪʃən/",
    "symbiosis": "/ˌsɪmbaɪˈoʊsɪs/",
    
    # Business
    "entrepreneur": "/ˌɑntrəprəˈnɜr/",
    "revenue": "/ˈrɛvəˌnu/",
    "stakeholder": "/ˈsteɪkˌhoʊldər/",
    "portfolio": "/pɔrtˈfoʊlioʊ/",
    "synergy": "/ˈsɪnərdʒi/",
    "leverage": "/ˈlɛvərɪdʒ/",
    "equity": "/ˈɛkwəti/",
    "margin": "/ˈmɑrdʒən/",
    "franchise": "/ˈfrænˌtʃaɪz/",
    "diversification": "/daɪˌvɜrsəfəˈkeɪʃən/",
    "acquisition": "/ˌækwəˈzɪʃən/",
    "liability": "/ˌlaɪəˈbɪləti/",
    "liquidate": "/ˈlɪkwəˌdeɪt/",
    "compliance": "/kəmˈplaɪəns/",
    "benchmark": "/ˈbɛnʧˌmɑrk/",
    "scalable": "/ˈskeɪləbəl/",
    "subsidiary": "/səbˈsɪdiˌɛri/",
    "turnover": "/ˈtɜrnˌoʊvər/",
    "valuation": "/ˌvæljuˈeɪʃən/",
    
    # Add more categories as needed...
}

# Difficulty levels for words
DIFFICULTY_LEVELS = {
    # General - Easy to Hard
    "efficient": "⭐",
    "authentic": "⭐",
    "versatile": "⭐⭐",
    "pragmatic": "⭐⭐",
    "resilient": "⭐⭐",
    "innovative": "⭐⭐",
    "profound": "⭐⭐",
    "coherent": "⭐⭐",
    "diligent": "⭐⭐",
    "benevolent": "⭐⭐⭐",
    "eloquent": "⭐⭐⭐",
    "meticulous": "⭐⭐⭐",
    "ubiquitous": "⭐⭐⭐",
    "ephemeral": "⭐⭐⭐",
    "ambiguous": "⭐⭐⭐",
    "tenacious": "⭐⭐⭐",
    "subtle": "⭐⭐⭐",
    "intricate": "⭐⭐⭐",
    "contemplative": "⭐⭐⭐",
    "serendipity": "⭐⭐⭐",
    
    # Science
    "gravity": "⭐",
    "molecule": "⭐",
    "ecosystem": "⭐⭐",
    "evolution": "⭐⭐",
    "catalyst": "⭐⭐",
    "enzyme": "⭐⭐",
    "neuron": "⭐⭐",
    "genome": "⭐⭐⭐",
    "hypothesis": "⭐⭐⭐",
    "photosynthesis": "⭐⭐⭐",
    "chromosome": "⭐⭐⭐",
    "quantum": "⭐⭐⭐",
    "biodiversity": "⭐⭐⭐",
    "metabolism": "⭐⭐⭐",
    "osmosis": "⭐⭐⭐",
    "mitosis": "⭐⭐⭐",
    "thermodynamics": "⭐⭐⭐",
    "isotope": "⭐⭐⭐",
    "radiation": "⭐⭐⭐",
    "symbiosis": "⭐⭐⭐",
}

def get_phonetic(word):
    """Get phonetic transcription for a word"""
    return PHONETICS.get(word.lower(), "")

def get_difficulty(word):
    """Get difficulty level for a word"""
    return DIFFICULTY_LEVELS.get(word.lower(), "⭐⭐")

def save_to_learned(word_entry, learned_file="learned.json"):
    """Save a word entry to learned.json file"""
    import json
    
    # Load existing learned words
    learned_words = []
    if os.path.exists(learned_file):
        try:
            with open(learned_file, 'r', encoding='utf-8') as f:
                learned_words = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            learned_words = []
    
    # Add timestamp to the entry
    import datetime
    word_entry_with_timestamp = word_entry.copy()
    word_entry_with_timestamp['learned_date'] = datetime.datetime.now().isoformat()
    
    # Check if word already exists in learned list
    existing_word = next((w for w in learned_words if w['word'].lower() == word_entry['word'].lower()), None)
    if not existing_word:
        learned_words.append(word_entry_with_timestamp)
        
        # Save back to file
        with open(learned_file, 'w', encoding='utf-8') as f:
            json.dump(learned_words, f, ensure_ascii=False, indent=2)
        return True
    return False

def load_learned_words(learned_file="learned.json"):
    """Load learned words from learned.json and convert to vocabulary format"""
    import json
    
    if not os.path.exists(learned_file):
        return []
    
    try:
        with open(learned_file, 'r', encoding='utf-8') as f:
            learned_words = json.load(f)
        
        # Convert to the same format as regular vocabulary
        formatted_words = []
        for word_entry in learned_words:
            formatted_word = {
                'word': word_entry.get('word', ''),
                'meaning': word_entry.get('meaning', ''),
                'phrase': word_entry.get('phrase', ''),
                'category': word_entry.get('category', 'general'),
                'learned_date': word_entry.get('learned_date', '')
            }
            formatted_words.append(formatted_word)
        
        return formatted_words
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_learned_words_to_file(learned_words, learned_file="learned.json"):
    """Save learned words back to JSON file"""
    import json
    
    with open(learned_file, 'w', encoding='utf-8') as f:
        json.dump(learned_words, f, ensure_ascii=False, indent=2)
    
    return True

def delete_word_from_file(word_to_delete, word_file):
    """Delete a word from the vocabulary file"""
    # Read all lines
    with open(word_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Filter out the word to delete
    updated_lines = []
    for line in lines:
        if line.strip():
            parts = line.strip().split(' | ')
            if len(parts) >= 1 and parts[0].lower() != word_to_delete.lower():
                updated_lines.append(line)
    
    # Write back to file
    with open(word_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    return True

def load_vocabulary_with_expressions(level):
    """Load vocabulary from JSON files with expressions included"""
    import json
    
    if level == "learned":
        return load_learned_words()
    
    # Map level to filename
    level_files = {
        1: "level1.json",
        2: "level2.json", 
        3: "level3.json"
    }
    
    filename = level_files.get(level)
    if not filename or not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten all categories into a single list
        all_words = []
        for category, words in data.items():
            for word_entry in words:
                # Add category to each word entry
                word_entry['category'] = category
                all_words.append(word_entry)
        
        return all_words
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def generate_quiz_question(words, correct_word):
    """Generate a multiple choice quiz question"""
    options = [correct_word]
    other_words = [w for w in words if w['word'] != correct_word['word']]
    
    # Add 3 random wrong options
    wrong_options = random.sample(other_words, min(3, len(other_words)))
    for word in wrong_options:
        options.append(word)
    
    random.shuffle(options)
    return options

# Configure the app
st.set_page_config(
    page_title="Vocabulary Builder - Advanced 1",
    page_icon="📚",
    layout="wide"
)

# Custom CSS to increase base font size by 80% for senior users (30% + 50% additional)
st.markdown("""
<style>
    .main .block-container {
        font-size: 1.95em;
    }
    
    .stSelectbox > div > div {
        font-size: 1.95em;
    }
    
    .stSelectbox label {
        font-size: 1.95em;
    }
    
    /* Main content selectboxes - make them smaller for better readability */
    .main .stSelectbox > div > div {
        font-size: 0.975em !important; /* Reduce selectbox content by 50% */
    }
    
    .main .stSelectbox > div > div > div {
        font-size: 0.975em !important; /* Reduce selected value display by 50% */
    }
    
    /* Additional targeting for main content selectboxes */
    .stApp .main .stSelectbox > div > div {
        font-size: 0.975em !important;
    }
    
    .stApp .main .stSelectbox > div > div > div {
        font-size: 0.975em !important;
    }
    
    .stApp .main .stSelectbox input {
        font-size: 0.975em !important;
    }
    
    /* Target selectbox by data attributes */
    [data-testid="stSelectbox"] > div > div {
        font-size: 0.975em !important;
    }
    
    [data-testid="stSelectbox"] > div > div > div {
        font-size: 0.975em !important;
    }
    
    /* Override all selectbox fonts in main content except sidebar */
    .stSelectbox:not(.css-1d391kg .stSelectbox) > div > div {
        font-size: 0.975em !important;
    }
    
    .stSelectbox:not(.css-1d391kg .stSelectbox) > div > div > div {
        font-size: 0.975em !important;
    }
    
    /* Direct targeting of main area selectboxes */
    .main .stSelectbox .stSelectbox {
        font-size: 0.975em !important;
    }
    
    /* Ensure all main content selectboxes are consistent across all modes */
    .main .block-container .stSelectbox > div > div {
        font-size: 0.975em !important;
    }
    
    .main .block-container .stSelectbox > div > div > div {
        font-size: 0.975em !important;
    }
    
    .main .block-container .stSelectbox input {
        font-size: 0.975em !important;
    }
    
    /* Ensure selectbox labels remain large and readable */
    .main .block-container .stSelectbox label {
        font-size: 1.95em !important;
    }
    
    .stRadio > div {
        font-size: 2.93em;
    }
    
    .stRadio > div > label {
        font-size: 2.25em;
    }
    
    .stButton > button {
        font-size: 1.95em;
        padding: 12px 24px;
    }
    
    .stMarkdown {
        font-size: 1.95em;
    }
    
    .stSubheader {
        font-size: 2.54em;
    }
    
    .stHeader {
        font-size: 3.12em;
    }
    
    .stTitle {
        font-size: 3.9em;
    }
    
    .stTextInput > div > div > input {
        font-size: 1.95em;
    }
    
    .stTextArea > div > div > textarea {
        font-size: 1.95em;
    }
    
    .stMetric {
        font-size: 1.95em;
    }
    
    .stInfo {
        font-size: 1.95em;
    }
    
    .stSuccess {
        font-size: 1.95em;
    }
    
    .stError {
        font-size: 1.95em;
    }
    
    .stWarning {
        font-size: 1.95em;
    }
    
    /* Sidebar styling - restored to original large sizes */
    .css-1d391kg {
        font-size: 1.95em;
    }
    
    /* Sidebar selectbox - both selected value and dropdown options reduced by 50% */
    .css-1d391kg .stSelectbox > div > div {
        font-size: 0.975em !important; /* Category dropdown options reduced by 50% */
    }
    
    .css-1d391kg .stSelectbox > div > div > div {
        font-size: 0.975em !important; /* Selected category value in box reduced by 50% */
    }
    
    .css-1d391kg .stSelectbox > div > div input {
        font-size: 0.975em !important; /* Input field text reduced by 50% */
    }
    
    .css-1d391kg .stSelectbox label {
        font-size: 2.925em; /* Label increased by 50% (1.95em × 1.5) */
    }
    
    /* Additional specificity for sidebar selectbox */
    .stSidebar .stSelectbox > div > div {
        font-size: 0.975em !important;
    }
    
    .stSidebar .stSelectbox > div > div > div {
        font-size: 0.975em !important;
    }
    
    /* Sidebar radio buttons - restored to large size */
    .css-1d391kg .stRadio > div {
        font-size: 2.93em;
    }
    
    .css-1d391kg .stRadio > div > label {
        font-size: 2.25em;
    }
    
    /* Sidebar markdown text - restored */
    .css-1d391kg .stMarkdown {
        font-size: 1.95em;
    }
    
    /* Sidebar title - restored */
    .css-1d391kg h1 {
        font-size: 1.95em;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.95em;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 Vocabulary Builder - Advanced 1")
st.header("Enhanced Learning with Phonetics & Quizzes")
st.subheader("Perfect for intermediate ESL learners")

# Main Menu Navigation
st.sidebar.title("🎯 Advanced Navigation")

# Level Selection
st.sidebar.markdown("### 🎯 Select Your Learning Level")
level_col1, level_col2, level_col3, level_col4, level_col5 = st.sidebar.columns(5)

with level_col1:
    if st.sidebar.button("📚 **Level 1: Beginner**\n\nBasic vocabulary", key="adv1_level1"):
        st.session_state.selected_level = 1

with level_col2:
    if st.sidebar.button("📖 **Level 2: Intermediate**\n\nChallenging words", key="adv1_level2"):
        st.session_state.selected_level = 2

with level_col3:
    if st.sidebar.button("📘 **Level 3: Advanced**\n\nSophisticated vocabulary", key="adv1_level3"):
        st.session_state.selected_level = 3

with level_col4:
    if st.sidebar.button("✅ **Learned Words**\n\nReview learned vocabulary", key="adv1_learned"):
        st.session_state.selected_level = "learned"

with level_col5:
    if st.sidebar.button("✅ **Korean Words**\n\nLearn Korean vocabulary", key="Korean"):
        st.session_state.selected_level = "Korean"

# Initialize session state
if 'selected_level' not in st.session_state:
    st.session_state.selected_level = 2  # Default to intermediate for Advanced 1 app

# Display current level
current_level = st.session_state.selected_level
if current_level == "learned":
    st.info(f"✅ **Current Level: Learned Words** - Review your mastered vocabulary")
else:
    # Map 'Korean' to 4 for LEVEL_DESCRIPTIONS
    level_key = 4 if current_level == "Korean" else current_level
    st.info(f"🎯 **Current Level: {current_level}** - {LEVEL_DESCRIPTIONS[level_key]}")

# Configuration
word_file = DEFAULT_VOCABULARY_FILE
category_list = DEFAULT_CATEGORIES

# Load sample vocabulary button
col1, col2 = st.columns(2)
with col1:
    if current_level == "learned":
        if st.button(f"📚 Load Learned Words", help="Load your learned vocabulary from learned.json"):
            learned_words = load_learned_words()
            if learned_words:
                # Convert learned words to the standard vocabulary format and save to the working file
                with open(word_file, "w", encoding='utf-8') as f:
                    for word_entry in learned_words:
                        f.write(f"{word_entry['word']} | {word_entry['meaning']} | {word_entry['phrase']} | {word_entry['category']}\n")
                st.success(f"✅ Successfully loaded {len(learned_words)} learned words!")
                st.info("Navigate to other sections to review your learned vocabulary.")
            else:
                st.warning("❌ No learned words found. Complete some lessons first to build your learned vocabulary!")
    else:
        if st.button(f"📚 Load Level {current_level} Vocabulary", help=f"Load 20 words for each category at Level {current_level}"):
            word_pools = load_word_pools(current_level)
            # print(f"Loaded word pools for Level {current_level}: {word_pools}")
            if word_pools:
                success = save_word_pools_to_file(word_pools, word_file)
                if success:
                    word_length = len(load_vocabulary_from_file(word_file))
                    print(f"Total words saved to {word_file}: {word_length}")
                    st.success(f"✅ Successfully loaded Level {current_level} vocabulary across all categories!")
                    #st.info("Navigate to other sections to explore the features.")
                else:
                    st.error("❌ Error loading sample vocabulary.")
            else:
                st.error(f"❌ Could not load Level {current_level} word pools from JSON file.")

with col2:
    # Statistics display
    all_words = load_vocabulary_from_file(word_file)
    if all_words:
        st.metric("📊 Total Words", len(all_words))

# Main navigation
select = st.sidebar.radio("Select Learning Mode", [
    "📖 Study Mode", 
    "🎯 Quiz Mode", 
    "➕ Add Word", 
    "📊 Progress"
])

# Category and speed selection for both Study Mode and Quiz Mode
if select in ["📖 Study Mode", "🎯 Quiz Mode"]:
    selected_category = st.sidebar.selectbox("Select a Category", category_list)
    
    # Speed selection as radio buttons
    st.sidebar.markdown("🔊 **Voice Speed:**")
    selected_speed = st.sidebar.radio(
        "Voice Speed Selection",
        options=SPEED_OPTIONS,
        format_func=lambda x: SPEED_LABELS[x],
        key="speed_radio",
        label_visibility="hidden"
    )
    
    # Quiz type selection for Quiz Mode
    if select == "🎯 Quiz Mode":
        st.sidebar.markdown("🎯 **Quiz Type:**")
        quiz_type = st.sidebar.radio(
            "Quiz Type Selection",
            ["Meaning → Word", "Word → Meaning"],
            key="quiz_type_radio",
            label_visibility="hidden"
        )

if select == "📖 Study Mode":
    st.subheader("📖 Enhanced Study Mode")

    # Filter selection
    difficulty_filter = st.sidebar.radio(
        "Filter by Difficulty:",
        ["All Levels", "⭐ Easy", "⭐⭐ Medium", "⭐⭐⭐ Hard"],
        horizontal=True
    )
    
    if selected_category:
        # Load vocabulary from vocabulary.txt for Study Mode
        all_words = load_vocabulary_from_file(word_file)
        filtered_words = filter_words_by_category(all_words, selected_category)
        # Apply difficulty filter
        if difficulty_filter != "All Levels":
            target_level = difficulty_filter
            filtered_words = [w for w in filtered_words if get_difficulty(w['word']) == target_level]
        if filtered_words:
            st.info(f"📚 Showing {len(filtered_words)} words from {selected_category}")
            for entry in filtered_words:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        difficulty = get_difficulty(entry['word'])
                        
                        # Simple card with visual border using Streamlit components
                        with st.container():
                            # Add a simple border using markdown
                            st.markdown("---")
                            
                            # Word title with emoji
                            st.markdown(f"### 📚 {entry['word']} {difficulty}")
                            
                            # Meaning
                            st.markdown(f"**Meaning:** {entry['meaning']}")
                            
                            # Expressions if available
                            expressions = entry.get('expressions')
                            if expressions:
                                st.markdown("**Simple Expressions:**")
                                for expr in expressions:
                                    st.markdown(f"• {expr}")
                            
                            # Example phrase
                            st.markdown(f"**Example Phrase:** {entry['phrase']}")
                            
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
                            if st.button(f"✏️ Change Phrase", key=f"edit_{entry['word']}", help="Edit example phrase"):
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
                                            success = update_phrase_in_json(entry['word'], new_phrase.strip(), current_level)
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
                            
                            # Bottom border
                            st.markdown("---")
                    
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Play buttons
                        if st.button(f"🔊 Word", key=f"word_{entry['word']}"):
                            audio_file = create_audio_file(entry['word'], f"word_{entry['word']}", is_phrase=False, speed=selected_speed)
                            if audio_file and os.path.exists(audio_file):
                                with open(audio_file, 'rb') as audio:
                                    # Detect audio format based on file extension
                                    audio_format = 'audio/mp3' if audio_file.endswith('.mp3') else 'audio/wav'
                                    st.audio(audio.read(), format=audio_format)
                                cleanup_audio_file(audio_file)
                            else:
                                st.error("Audio generation failed")
                        
                        if entry['phrase'] and st.button(f"🔊 Phrase", key=f"phrase_{entry['word']}"):
                            audio_file = create_audio_file(entry['phrase'], f"phrase_{entry['word']}", is_phrase=True, speed=selected_speed)
                            if audio_file and os.path.exists(audio_file):
                                with open(audio_file, 'rb') as audio:
                                    # Detect audio format based on file extension
                                    audio_format = 'audio/mp3' if audio_file.endswith('.mp3') else 'audio/wav'
                                    st.audio(audio.read(), format=audio_format)
                                cleanup_audio_file(audio_file)
                            else:
                                st.error("Audio generation failed")
                        
                        # Action buttons
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Different buttons based on current level
                        if current_level == "learned":
                            # Move back to vocabulary button for learned words
                            if st.button(f"↩️ Move Back", key=f"moveback_{entry['word']}", help="Move back to main vocabulary"):
                                # Add word back to main vocabulary file
                                with open(word_file, "a", encoding='utf-8') as f:
                                    f.write(f"{entry['word']} | {entry['meaning']} | {entry['phrase']} | {entry['category']}\n")
                                
                                # Remove from learned.json
                                learned_words = load_learned_words()
                                updated_learned = [w for w in learned_words if w['word'].lower() != entry['word'].lower()]
                                save_learned_words_to_file(updated_learned)
                                
                                st.success(f"'{entry['word']}' moved back to main vocabulary!")
                                st.rerun()  # Refresh the page to update the list
                        else:
                            # Learned button for regular levels
                            if st.button(f"✅ Learned", key=f"learned_{entry['word']}", help="Move to learned words"):
                                success = save_to_learned(entry)
                                if success:
                                    delete_word_from_file(entry['word'], word_file)
                                    st.success(f"'{entry['word']}' moved to learned words!")
                                    st.rerun()  # Refresh the page to update the list
                                else:
                                    st.warning(f"'{entry['word']}' is already in learned words.")
                        
                        # Delete button (available for all levels)
                        if st.button(f"🗑️ Delete", key=f"delete_{entry['word']}", help="Delete this word"):
                            if current_level == "learned":
                                # Delete from learned.json
                                learned_words = load_learned_words()
                                updated_learned = [w for w in learned_words if w['word'].lower() != entry['word'].lower()]
                                save_learned_words_to_file(updated_learned)
                            else:
                                # Delete from main vocabulary file
                                delete_word_from_file(entry['word'], word_file)
                            
                            st.success(f"'{entry['word']}' deleted successfully!")
                            st.rerun()  # Refresh the page to update the list
        else:
            st.info("No words found for the selected category and difficulty level.")

elif select == "🎯 Quiz Mode":
    st.subheader("🎯 Interactive Quiz Mode")
    
    # Initialize session state for quiz
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'quiz_total' not in st.session_state:
        st.session_state.quiz_total = 0
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    
    # Load words for quiz using sidebar selections with expressions
    all_words = load_vocabulary_with_expressions(current_level)
    quiz_words = filter_words_by_category(all_words, selected_category)
    
    # Display current quiz settings
    st.info(f"📚 **Category:** {selected_category} | 🎯 **Quiz Type:** {quiz_type}")
    
    if quiz_words and len(quiz_words) >= 4:
        # Score display
        if st.session_state.quiz_total > 0:
            accuracy = (st.session_state.quiz_score / st.session_state.quiz_total) * 100
            st.metric("Quiz Accuracy", f"{accuracy:.1f}%", f"{st.session_state.quiz_score}/{st.session_state.quiz_total}")
        
        # Generate new question button
        if st.button("🎲 New Question") or st.session_state.current_question is None:
            correct_word = random.choice(quiz_words)
            options = generate_quiz_question(quiz_words, correct_word)
            st.session_state.current_question = {
                'correct': correct_word,
                'options': options,
                'answered': False
            }
        
        # Display current question
        if st.session_state.current_question:
            question = st.session_state.current_question
            correct_word = question['correct']
            
            if quiz_type == "Meaning → Word":
                st.markdown(f'<h3 style="font-size: 2.4em;">What word has this meaning?</h3>', unsafe_allow_html=True)
                st.markdown(f'<div style="background-color: #d1ecf1; padding: 15px; border-radius: 10px; border-left: 5px solid #0c5460; font-size: 1.95em;"><strong>Meaning:</strong> {correct_word["meaning"]}</div>', unsafe_allow_html=True)
                
                # Multiple choice options
                option_labels = [opt['word'] for opt in question['options']]
            else:  # Word → Meaning
                st.markdown(f'<h3 style="font-size: 2.4em;">What is the meaning of: <strong>{correct_word["word"]}</strong></h3>', unsafe_allow_html=True)
                
                # Multiple choice options
                option_labels = [opt['meaning'] for opt in question['options']]
            
            # Radio button for answer selection
            if not question['answered']:
                st.markdown('<p style="font-size: 1.95em; font-weight: bold; margin-top: 20px;">Choose your answer:</p>', unsafe_allow_html=True)
                selected_answer = st.radio(
                    "Answer Selection",
                    option_labels,
                    key="quiz_answer",
                    label_visibility="hidden"
                )
                
                if st.button("✅ Submit Answer"):
                    # Check if answer is correct
                    if quiz_type == "Meaning → Word":
                        is_correct = selected_answer == correct_word['word']
                    else:
                        is_correct = selected_answer == correct_word['meaning']
                    
                    # Update score
                    st.session_state.quiz_total += 1
                    if is_correct:
                        st.session_state.quiz_score += 1
                        st.success("🎉 Correct! Well done!")
                    else:
                        st.error(f"❌ Incorrect. The correct answer was: **{correct_word['word'] if quiz_type == 'Meaning → Word' else correct_word['meaning']}**")
                    
                    # Mark as answered
                    st.session_state.current_question['answered'] = True
                    
                    # Show word details with new structure
                    difficulty = get_difficulty(correct_word['word'])
                    
                    # Simple quiz result card
                    st.success("Word Details:")
                    
                    with st.container():
                        # Simple border for quiz result
                        st.markdown("---")
                        
                        # Word title with emoji
                        st.markdown(f"### 📚 {correct_word['word']} {difficulty}")
                        
                        # Meaning
                        st.markdown(f"**Meaning:** {correct_word['meaning']}")
                        
                        # Expressions if available
                        expressions = correct_word.get('expressions', [])
                        if expressions:
                            st.markdown("**Simple Expressions:**")
                            for expr in expressions:
                                st.markdown(f"• {expr}")
                        
                        # Example phrase
                        if correct_word['phrase']:
                            st.markdown(f"**💡 Example:** {correct_word['phrase']}")
                        
                        # Display media if exists (image or video)
                        media_path = correct_word.get('media')
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
                                    st.image(media_path, caption=f"Visual for: {correct_word['phrase']}", use_column_width=True)
                                except Exception as e:
                                    st.error(f"Error loading image: {str(e)}")
                            else:
                                st.warning(f"Unsupported media format: {file_extension}")
                        
                        # Bottom border
                        st.markdown("---")
    else:
        st.warning("Need at least 4 words in the selected category to run quiz mode. Please load sample vocabulary first.")

elif select == "➕ Add Word":
    st.subheader("➕ Add New Word with Enhanced Features")
    
    col1, col2 = st.columns(2)
    with col1:
        word = st.text_input("Enter the word:")
        meaning = st.text_area("Enter the meaning:")
    with col2:
        phrase = st.text_input("Enter an example phrase:")
        category = st.selectbox("Select Category", category_list)
        # phonetic_input = st.text_input("Phonetic transcription (optional):", placeholder="e.g., /ˈɛksəmpl/")
        difficulty_level = st.selectbox("Difficulty Level", ["⭐ Easy", "⭐⭐ Medium", "⭐⭐⭐ Hard"])
    
    if st.button("➕ Add Word"):
        is_valid, error_msg = validate_word_entry(word, meaning, phrase, category.lower())
        
        if is_valid:
            st.success(f"Word '{word}' added successfully!")
            # Note: In a full implementation, you'd also save the phonetic and difficulty data
            with open(word_file, "a", encoding='utf-8') as f:
                f.write(f"{word} | {meaning} | {phrase} | {category.lower()}\n")
        else:
            st.error(error_msg)

elif select == "📊 Progress":
    st.subheader("📊 Learning Progress & Statistics")
    
    all_words = load_vocabulary_from_file(word_file)
    
    if all_words:
        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Words", len(all_words))
        with col2:
            if st.session_state.quiz_total > 0:
                accuracy = (st.session_state.quiz_score / st.session_state.quiz_total) * 100
                st.metric("Quiz Accuracy", f"{accuracy:.1f}%")
            else:
                st.metric("Quiz Accuracy", "No quizzes yet")
        with col3:
            st.metric("Quizzes Taken", st.session_state.quiz_total)
        with col4:
            st.metric("Correct Answers", st.session_state.quiz_score)
        
        # Category breakdown
        st.markdown("### 📈 Words by Category")
        category_stats = {}
        for word in all_words:
            cat = word.get('category', 'Unknown').title()
            category_stats[cat] = category_stats.get(cat, 0) + 1
        
        # Display as columns
        cols = st.columns(len(category_stats))
        for i, (category, count) in enumerate(category_stats.items()):
            with cols[i]:
                st.metric(category, count)
        
        # Difficulty distribution (if available)
        st.markdown("### ⭐ Difficulty Distribution")
        difficulty_stats = {"⭐ Easy": 0, "⭐⭐ Medium": 0, "⭐⭐⭐ Hard": 0}
        for word in all_words:
            diff = get_difficulty(word['word'])
            if diff in difficulty_stats:
                difficulty_stats[diff] += 1
        
        diff_cols = st.columns(3)
        for i, (level, count) in enumerate(difficulty_stats.items()):
            with diff_cols[i]:
                st.metric(level, count)
        
        # Reset progress button
        if st.button("🔄 Reset Quiz Progress"):
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = 0
            st.success("Quiz progress reset!")
    else:
        st.info("Load vocabulary words to see progress statistics.")

# Footer
st.markdown("---")
st.markdown("**Advanced 1 Features:** Phonetic transcription, difficulty levels, interactive quizzes, progress tracking")