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

# Premium Modern UI/UX CSS Design Tokens
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #221b15 0%, #120e0b 60%, #0a0806 100%);
        color: #f6f2eb;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }
    
    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(224, 169, 109, 0.12) 0%, rgba(90, 62, 43, 0.25) 50%, rgba(30, 22, 16, 0.6) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(224, 169, 109, 0.3);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 28px;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5), inset 0 1px 1px 0 rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #fff7ed, #e0a96d, #fef3c7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: #cbb49e;
        font-size: 1.05rem;
        margin-top: 4px;
        font-weight: 400;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.35);
        color: #4ade80;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 10px #22c55e;
    }

    /* Menu Card items */
    .menu-card {
        background: rgba(26, 21, 17, 0.75);
        border: 1px solid rgba(224, 169, 109, 0.18);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .menu-card:hover {
        border-color: #e0a96d;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    .menu-item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    
    .menu-name {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 1.08rem;
        color: #fff7ed;
    }
    
    .menu-price {
        font-weight: 700;
        color: #e0a96d;
        background: rgba(224, 169, 109, 0.15);
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 0.92rem;
        border: 1px solid rgba(224, 169, 109, 0.25);
    }
    
    .menu-desc {
        font-size: 0.86rem;
        color: #baaa9b;
        margin-bottom: 10px;
        line-height: 1.4;
    }
    
    .badge {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 5px;
        margin-bottom: 4px;
    }
    
    .badge-hot { background: rgba(239, 68, 68, 0.18); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.35); }
    .badge-cold { background: rgba(59, 130, 246, 0.18); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.35); }
    .badge-allergen { background: rgba(245, 158, 11, 0.18); color: #fde047; border: 1px solid rgba(245, 158, 11, 0.35); }
    .badge-safe { background: rgba(34, 197, 94, 0.18); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.35); }

    /* Buttons & Interactive Elements */
    .stButton > button {
        background: linear-gradient(135deg, rgba(224, 169, 109, 0.12) 0%, rgba(140, 95, 58, 0.18) 100%);
        color: #fff7ed;
        border: 1px solid rgba(224, 169, 109, 0.3);
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
        width: 100%;
        text-align: left;
        padding: 10px 16px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(224, 169, 109, 0.25) 0%, rgba(140, 95, 58, 0.35) 100%);
        border-color: #e0a96d;
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(224, 169, 109, 0.2);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #120e0b;
        border-right: 1px solid rgba(224, 169, 109, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# Load Menu
@st.cache_data
def load_menu():
    try:
        with open("menu.json", "r") as f:
            return json.load(f)
    except Exception:
        return []

menu_items = load_menu()

# API Key & Environment Checks
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("true", "1")

# Sidebar - Live Interactive Menu & Configuration
with st.sidebar:
    st.markdown("<h2 style='font-family: Outfit; font-size: 1.4rem; color: #e0a96d; margin-bottom: 0;'>☕ Menu & Allergen Guide</h2>", unsafe_allow_html=True)
    st.caption("Live source of truth for prices and allergens")
    
    # Filter Tabs & Search
    search_query = st.text_input("🔍 Search menu items...", placeholder="e.g. Chai, Cold Brew, Milk-free")
    
    filtered_items = menu_items
    if search_query:
        sq = search_query.lower()
        filtered_items = [
            i for i in menu_items 
            if sq in i["name"].lower() or sq in i["description"].lower() or any(sq in t.lower() for t in i.get("tags", []))
        ]

    for item in filtered_items:
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
    st.markdown("<h3 style='font-family: Outfit; font-size: 1.1rem; color: #e0a96d;'>⚙️ Configuration</h3>", unsafe_allow_html=True)
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
    <div>
        <h1 class="hero-title">☕🫖 Desi AI Barista</h1>
        <div class="hero-subtitle">Authentic Indian Coffee & Chai House • Powered by Google ADK & Vector RAG</div>
    </div>
    <div class="status-badge">
        <div class="pulse-dot"></div>
        <span>Cafe Open & Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Suggestion Chips
st.markdown("<h5 style='font-family: Outfit; color: #e0a96d; margin-bottom: 12px;'>💡 Quick Recommendation Prompts:</h5>", unsafe_allow_html=True)
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
        with st.spinner("Searching coffee knowledge & verifying menu..."):
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
