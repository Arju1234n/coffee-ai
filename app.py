import os
import json
import asyncio
import streamlit as st

from google.adk.runners import InMemoryRunner
from google.genai import types

from agent import root_agent

# Page Configuration
st.set_page_config(
    page_title="Desi AI Barista ☕🫖",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom Styling (Vanilla CSS with Warm Coffee Design Tokens & Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #131110 0%, #1c1815 50%, #251e19 100%);
        color: #f3efe6;
    }
    
    /* Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(212, 163, 115, 0.15) 0%, rgba(186, 117, 70, 0.25) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(212, 163, 115, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: center;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #fefae0, #d4a373, #faedcd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .hero-subtitle {
        color: #cca885;
        font-size: 1.05rem;
        margin-top: 6px;
    }

    /* Menu Card items */
    .menu-card {
        background: rgba(35, 29, 24, 0.7);
        border: 1px solid rgba(212, 163, 115, 0.2);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .menu-card:hover {
        border-color: #d4a373;
        transform: translateY(-2px);
    }
    
    .menu-item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
    }
    
    .menu-name {
        font-weight: 600;
        font-size: 1.05rem;
        color: #fefae0;
    }
    
    .menu-price {
        font-weight: 700;
        color: #d4a373;
        background: rgba(212, 163, 115, 0.15);
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.9rem;
    }
    
    .menu-desc {
        font-size: 0.85rem;
        color: #bfa893;
        margin-bottom: 6px;
    }
    
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 4px;
        text-transform: lowercase;
    }
    
    .badge-hot { background: rgba(235, 94, 85, 0.2); color: #ff8b84; border: 1px solid rgba(235, 94, 85, 0.4); }
    .badge-cold { background: rgba(84, 160, 255, 0.2); color: #82c0ff; border: 1px solid rgba(84, 160, 255, 0.4); }
    .badge-allergen { background: rgba(255, 177, 66, 0.2); color: #ffd175; border: 1px solid rgba(255, 177, 66, 0.4); }
    .badge-safe { background: rgba(46, 213, 115, 0.2); color: #7bed9f; border: 1px solid rgba(46, 213, 115, 0.4); }

    /* Quick Suggestion Pills */
    .stButton > button {
        background: rgba(212, 163, 115, 0.12);
        color: #fefae0;
        border: 1px solid rgba(212, 163, 115, 0.3);
        border-radius: 20px;
        font-weight: 500;
        transition: all 0.2s ease;
        width: 100%;
        text-align: left;
        padding: 8px 14px;
    }
    
    .stButton > button:hover {
        background: rgba(212, 163, 115, 0.25);
        border-color: #d4a373;
        color: #ffffff;
        transform: scale(1.01);
    }
</style>
""", unsafe_allow_html=True)

# Load Menu for Sidebar Preview
@st.cache_data
def load_menu():
    try:
        with open("menu.json", "r") as f:
            return json.load(f)
    except Exception:
        return []

menu_items = load_menu()

# Environment / API Key setup check
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("true", "1")

# Sidebar Implementation
with st.sidebar:
    st.markdown("### ☕ Menu Overview")
    st.caption("Live source of truth for pricing & allergens")
    
    for item in menu_items:
        tags_html = ""
        for tag in item.get("tags", []):
            b_class = "badge-hot" if tag == "hot" else ("badge-cold" if tag == "cold" else "badge-safe")
            tags_html += f'<span class="badge {b_class}">{tag}</span>'
            
        allergen_text = ", ".join(item.get("allergens", []))
        if allergen_text:
            tags_html += f'<span class="badge badge-allergen">⚠️ {allergen_text}</span>'
        else:
            tags_html += '<span class="badge badge-safe">🌱 milk-free</span>'

        st.markdown(f"""
        <div class="menu-card">
            <div class="menu-item-header">
                <span class="menu-name">{item['name']}</span>
                <span class="menu-price">₹{item['price']}</span>
            </div>
            <div class="menu-desc">{item['description']}</div>
            <div>{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    if not api_key and not use_vertex:
        user_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key.")
        if user_key:
            os.environ["GEMINI_API_KEY"] = user_key
            st.success("API Key saved!")
            
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main Header Banner
st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">☕🫖 Desi AI Barista</h1>
    <div class="hero-subtitle">Authentic Indian Coffee & Chai House Powered by Google ADK & Vector RAG</div>
</div>
""", unsafe_allow_html=True)

# Quick Suggestion Chips
st.markdown("##### 💡 Quick Suggestions:")
col1, col2, col3, col4 = st.columns(4)

selected_prompt = None
with col1:
    if st.button("☕ South Indian Filter Coffee"):
        selected_prompt = "Tell me about South Indian Filter Coffee price and ingredients."
with col2:
    if st.button("🫖 Desi Masala Chai"):
        selected_prompt = "I want a warm spiced Indian tea with milk."
with col3:
    if st.button("🧊 Cold Strong (Milk-Free) <₹250"):
        selected_prompt = "I want a cold strong coffee under ₹250 and I am allergic to milk."
with col4:
    if st.button("🥛 Kesar Badam Milk"):
        selected_prompt = "Recommend a rich traditional Indian sweet drink."


# Session State Initialization
if "runner" not in st.session_state:
    st.session_state.runner = InMemoryRunner(
        agent=root_agent,
        app_name="coffee_ai"
    )

if "user_id" not in st.session_state:
    st.session_state.user_id = "customer_1"

if "session_id" not in st.session_state:
    session = asyncio.run(
        st.session_state.runner.session_service.create_session(
            app_name="coffee_ai",
            user_id=st.session_state.user_id
        )
    )
    st.session_state.session_id = session.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "☕"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# User Input
chat_input_val = st.chat_input("Ask me about coffee recommendations, budget, or allergies...")
user_input = selected_prompt or chat_input_val

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    async def get_response():
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )

        response_text = ""
        async for event in st.session_state.runner.run_async(
            user_id=st.session_state.user_id,
            session_id=st.session_state.session_id,
            new_message=content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        return response_text

    with st.chat_message("assistant", avatar="☕"):
        with st.spinner("Searching coffee knowledge & checking menu..."):
            try:
                response = asyncio.run(get_response())
            except Exception as e:
                if "No API key was provided" in str(e) or "API key" in str(e):
                    response = "⚠️ **API Key Required**: No Gemini API key found. Please set `export GEMINI_API_KEY='your_key'` in your terminal or enter it in the sidebar settings."
                else:
                    response = f"⚠️ An error occurred: {str(e)}"
            st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
