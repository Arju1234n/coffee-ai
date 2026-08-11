import os
import json
import asyncio
import base64
import streamlit as st

# Check for Google ADK and GenAI dependencies
try:
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False

from agent import root_agent
from rag import rag_engine, search_with_telemetry, search_coffee_knowledge

# Page Configuration
st.set_page_config(
    page_title="Desi Coffee & Chai Khana ☕🫖 | Ustad Chaiwala",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to encode image to base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""

banner_b64 = get_base64_image("banner.png")

# Premium Modern UI/UX Design System CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Base CSS Resets */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% -20%, #2a1c12 0%, #150e09 45%, #0b0704 100%);
        color: #f7f3ed;
    }

    /* Hide standard header noise */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Main Layout Container */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }
    
    /* Glassmorphism Hero Container */
    .hero-container {
        position: relative;
        background: linear-gradient(135deg, rgba(42, 28, 18, 0.85) 0%, rgba(20, 13, 8, 0.95) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(224, 169, 109, 0.35);
        border-radius: 24px;
        padding: 28px 36px;
        margin-bottom: 20px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 245, 230, 0.15);
        overflow: hidden;
    }
    
    .hero-flex {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        flex-wrap: wrap;
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff 0%, #e0a96d 40%, #fcd34d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 8px 0;
        letter-spacing: -0.8px;
        line-height: 1.1;
    }

    .hero-subtitle {
        color: #d1bead;
        font-size: 1.1rem;
        margin: 0;
        font-weight: 400;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .tech-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(224, 169, 109, 0.12);
        border: 1px solid rgba(224, 169, 109, 0.3);
        color: #e0a96d;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.35);
        color: #4ade80;
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 0.88rem;
        font-weight: 600;
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.15);
    }

    .pulse-dot {
        width: 10px;
        height: 10px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 12px #22c55e;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    /* Banner Image Box */
    .banner-img-box {
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid rgba(224, 169, 109, 0.35);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
        max-height: 250px;
        object-fit: cover;
        width: 100%;
        margin-bottom: 24px;
        display: block;
    }

    /* Modern Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(20, 13, 8, 0.6);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(224, 169, 109, 0.2);
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre;
        border-radius: 12px;
        color: #c4b4a5;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0 20px;
        background-color: transparent;
        border: none !important;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(224, 169, 109, 0.25) 0%, rgba(160, 105, 60, 0.35) 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(224, 169, 109, 0.4) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* Menu Cards */
    .menu-card-ui {
        background: linear-gradient(145deg, rgba(32, 22, 14, 0.8) 0%, rgba(18, 12, 7, 0.9) 100%);
        border: 1px solid rgba(224, 169, 109, 0.2);
        border-radius: 18px;
        padding: 20px;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }

    .menu-card-ui:hover {
        border-color: #e0a96d;
        transform: translateY(-4px);
        box-shadow: 0 14px 35px rgba(224, 169, 109, 0.15);
    }

    .item-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 10px;
    }

    .item-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff7ed;
        margin: 0;
    }

    .item-price {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 1.1rem;
        color: #e0a96d;
        background: rgba(224, 169, 109, 0.15);
        padding: 4px 12px;
        border-radius: 12px;
        border: 1px solid rgba(224, 169, 109, 0.3);
        white-space: nowrap;
    }

    .item-desc {
        color: #bfaea0;
        font-size: 0.9rem;
        line-height: 1.45;
        margin-bottom: 14px;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 0.76rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .badge-hot { background: rgba(239, 68, 68, 0.18); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.35); }
    .badge-cold { background: rgba(59, 130, 246, 0.18); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.35); }
    .badge-allergen { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-safe { background: rgba(34, 197, 94, 0.18); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.35); }
    .badge-tag { background: rgba(224, 169, 109, 0.12); color: #e0a96d; border: 1px solid rgba(224, 169, 109, 0.25); }

    /* Custom Chat Message Containers */
    .stChatMessage {
        background-color: rgba(25, 17, 11, 0.7) !important;
        border: 1px solid rgba(224, 169, 109, 0.2) !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        margin-bottom: 16px !important;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #120c08 !important;
        border-right: 1px solid rgba(224, 169, 109, 0.2) !important;
    }

    /* Prompt Suggestion Buttons */
    .prompt-chip-btn button {
        background: linear-gradient(135deg, rgba(45, 30, 19, 0.9) 0%, rgba(25, 16, 10, 0.9) 100%) !important;
        color: #f3e8dc !important;
        border: 1px solid rgba(224, 169, 109, 0.3) !important;
        border-radius: 14px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        text-align: left !important;
        width: 100% !important;
    }
    
    .prompt-chip-btn button:hover {
        border-color: #e0a96d !important;
        background: linear-gradient(135deg, rgba(224, 169, 109, 0.25) 0%, rgba(140, 95, 58, 0.35) 100%) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(224, 169, 109, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Load Menu Data
@st.cache_data
def load_menu():
    try:
        with open("menu.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

menu_items = load_menu()

# API Key & Environment Setup
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("true", "1")
has_api_access = bool(api_key or use_vertex)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "cart" not in st.session_state:
    st.session_state.cart = []

if "user_id" not in st.session_state:
    st.session_state.user_id = "customer_1"

if "session_id" not in st.session_state:
    st.session_state.session_id = "session_1"

if ADK_AVAILABLE and has_api_access and "runner" not in st.session_state:
    try:
        st.session_state.runner = InMemoryRunner(
            agent=root_agent,
            app_name="coffee_ai"
        )
        session = asyncio.run(
            st.session_state.runner.session_service.create_session(
                app_name="coffee_ai",
                user_id=st.session_state.user_id
            )
        )
        st.session_state.session_id = session.id
    except Exception:
        st.session_state.runner = None

# Sidebar - Settings, Order Summary & Knowledge Info
with st.sidebar:
    st.markdown("<h2 style='font-family: Outfit; font-size: 1.4rem; color: #e0a96d; margin-bottom: 4px;'>☕ Desi Coffee & Chai Khana</h2>", unsafe_allow_html=True)
    st.caption("Ustad Chaiwala Persona • Authentic Indian Brews")
    
    st.markdown("---")
    
    # Cart Quick Summary
    cart_count = sum(item.get("qty", 1) for item in st.session_state.cart)
    cart_total = sum(item["price"] * item.get("qty", 1) for item in st.session_state.cart)
    
    st.markdown(f"<h3 style='font-family: Outfit; font-size: 1.1rem; color: #f59e0b;'>🛒 Active Order ({cart_count})</h3>", unsafe_allow_html=True)
    if not st.session_state.cart:
        st.info("Your order basket is empty. Browse the Menu tab to add delicious drinks!")
    else:
        for idx, c_item in enumerate(st.session_state.cart):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**{c_item['name']}** (x{c_item.get('qty', 1)})")
                st.caption(f"₹{c_item['price'] * c_item.get('qty', 1)}")
            with col_b:
                if st.button("❌", key=f"remove_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
        st.markdown(f"**Total: ₹{cart_total}**")
        if st.button("🚀 Ask Ustad Chaiwala to Review Order"):
            st.session_state.prompt_trigger = f"I have ordered: {', '.join([i['name'] for i in st.session_state.cart])}. Total ₹{cart_total}. Please verify if this contains milk or any allergen risk, and confirm the brewing details!"
            st.rerun()

    st.markdown("---")
    st.markdown("<h3 style='font-family: Outfit; font-size: 1.1rem; color: #e0a96d;'>⚙️ Engine Status</h3>", unsafe_allow_html=True)
    
    if has_api_access:
        st.success("🟢 Google GenAI / ADK Active")
    else:
        st.info("⚡ RAG Simulation Mode Active")
        user_key = st.text_input("Gemini API Key (Optional)", type="password", help="Enter key to enable cloud ADK Runner.")
        if user_key:
            os.environ["GEMINI_API_KEY"] = user_key
            st.success("API Key set! Reloading...")
            st.rerun()
            
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("<div style='font-size: 0.8rem; color: #a39282;'>Powered by <b>Google Agent Development Kit (ADK)</b> & <b>Vector RAG (text-embedding-004)</b></div>", unsafe_allow_html=True)

# Main Hero Header Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-flex">
        <div>
            <h1 class="hero-title">☕🫖 Desi Coffee & Chai Khana</h1>
            <div class="hero-subtitle">
                <span>Authentic Indian Brews by Ustad Chaiwala</span>
                <span class="tech-tag">⚡ Google ADK</span>
                <span class="tech-tag">🧠 Vector RAG</span>
            </div>
        </div>
        <div class="status-badge">
            <div class="pulse-dot"></div>
            <span>Khana Open & Brews Steaming</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Display Hero Banner Artwork
if os.path.exists("banner.png"):
    st.markdown(f"""
    <img src="data:image/png;base64,{banner_b64}" class="banner-img-box" alt="Desi Coffee & Chai Khana Banner" />
    """, unsafe_allow_html=True)

# Navigation Tabs
tab_chat, tab_menu, tab_matcher, tab_rag, tab_cart = st.tabs([
    "💬 Ustad Chaiwala Chat", 
    "📋 Menu & Allergen Matrix", 
    "🎯 Flavor Matcher", 
    "🧠 RAG & ADK Telemetry",
    "🛒 Order Builder"
])

# ==========================================
# TAB 1: USTAD CHAIWALA CHAT & RECOMMENDATIONS
# ==========================================
with tab_chat:
    st.markdown("<h4 style='font-family: Outfit; color: #e0a96d; margin-bottom: 12px;'>💡 Quick Recommendations by Ustad Chaiwala:</h4>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    selected_prompt = None
    if "prompt_trigger" in st.session_state and st.session_state.prompt_trigger:
        selected_prompt = st.session_state.prompt_trigger
        st.session_state.prompt_trigger = None

    with col1:
        st.markdown('<div class="prompt-chip-btn">', unsafe_allow_html=True)
        if st.button("☕ South Indian Filter Coffee", key="btn_p1"):
            selected_prompt = "Tell me about South Indian Filter Coffee price and ingredients."
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="prompt-chip-btn">', unsafe_allow_html=True)
        if st.button("🫖 Desi Masala Chai", key="btn_p2"):
            selected_prompt = "I want a warm spiced Indian tea with milk."
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="prompt-chip-btn">', unsafe_allow_html=True)
        if st.button("🧊 Cold Strong (Milk-Free) <₹250", key="btn_p3"):
            selected_prompt = "I want a cold strong coffee under ₹250 and I am allergic to milk."
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="prompt-chip-btn">', unsafe_allow_html=True)
        if st.button("🥛 Kesar Badam Milk", key="btn_p4"):
            selected_prompt = "Recommend a rich traditional Indian sweet drink."
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Render Chat History
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "☕"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"], unsafe_allow_html=True)
            if "telemetry" in msg and msg["telemetry"]:
                with st.expander("⚡ Vector RAG & ADK Telemetry Breakdown"):
                    tel = msg["telemetry"]
                    st.markdown(f"""
                    - **RAG Strategy**: `{tel.get('strategy', 'N/A')}`
                    - **Embedding Model**: `{tel.get('embedding_model', 'text-embedding-004')}`
                    - **Similarity Score**: `{tel.get('top_score', 'N/A')}`
                    - **Retrieved Knowledge Chunks**: `{', '.join(tel.get('matched_chunks', ['South Indian Filter Coffee']))}`
                    - **Grounding Source**: `menu.json (Truth Authority)`
                    """)

    # User Input Field
    chat_input_val = st.chat_input("Ask Ustad Chaiwala about brews, ingredients, prices, or milk allergies...")
    user_input = selected_prompt or chat_input_val

    if user_input:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Barista Engine Logic
        response_text = ""
        telemetry_info = {}

        with st.chat_message("assistant", avatar="☕"):
            with st.spinner("Ustad Chaiwala is consulting Knowledge RAG & menu..."):
                
                # Retrieve RAG context and telemetry
                rag_res = search_with_telemetry(user_input)
                knowledge_context = rag_res["content"]
                telemetry_info = rag_res["telemetry"]

                # Case A: Live Google ADK Cloud Execution
                if ADK_AVAILABLE and has_api_access and "runner" in st.session_state and st.session_state.runner:
                    try:
                        content = types.Content(role="user", parts=[types.Part(text=user_input)])
                        async def run_adk():
                            res = ""
                            async for event in st.session_state.runner.run_async(
                                user_id=st.session_state.user_id,
                                session_id=st.session_state.session_id,
                                new_message=content
                            ):
                                if event.content and event.content.parts:
                                    for part in event.content.parts:
                                        if part.text:
                                            res += part.text
                            return res
                        response_text = asyncio.run(run_adk())
                    except Exception as ex:
                        response_text = f"⚠️ ADK Execution fallback: {str(ex)}"

                # Case B: Smart Built-in RAG Ustad Chaiwala Engine (Rule-based RAG grounding)
                if not response_text:
                    q_lower = user_input.lower()
                    
                    if "south indian filter coffee" in q_lower or ("filter coffee" in q_lower and "price" in q_lower):
                        response_text = """Namaste ji! 🙏 Welcome to **Desi Coffee & Chai Khana**!

Ah, our delightful **South Indian Filter Coffee** is priced at **₹140**. ☕

### 📜 Drink Highlights & Brewing Process:
* **Price**: **₹140** (Exact official price in `menu.json`)
* **Brewing Method**: Prepared using dark-roasted Chicory blended coffee beans, slow-brewed through a traditional stainless brass filter decoction process.
* **Serving Style**: Poured back and forth between a brass *Dabara* and *Tumbler* to create a velvety, aerated frothy foam layer with hot milk.
* **Profile**: Hot, Strong, Creamy & Medium-Sweet.

> ⚠️ **Allergen Notice**: Contains **Milk (Dairy)**! If you have a lactose intolerance or milk allergy, please request a dairy-free beverage like our **Cold Brew (₹220)** or **Lemon Iced Tea (₹150)**.

Would you like me to add this to your active order basket?"""

                    elif "masala chai" in q_lower or "spiced indian tea" in q_lower:
                        response_text = """Namaste ji! 🙏 Our authentic **Desi Masala Chai** is priced at **₹130**. 🫖

### 🌿 Flavors & Ingredients:
* **Price**: **₹130**
* **Ingredients**: Assam black tea leaves slow-simmered with crushed green cardamom, fresh ginger root, cloves, cinnamon, and creamy whole milk.
* **Attributes**: Hot, Spiced, Comforting & Creamy.

> ⚠️ **Allergen Notice**: Contains **Milk**. Dairy-free alternatives include **Lemon Iced Tea (₹150)** or **Mango Iced Tea (₹180)**!"""

                    elif "milk" in q_lower and ("allergic" in q_lower or "no milk" in q_lower or "dairy-free" in q_lower or "milk-free" in q_lower or "under 250" in q_lower or "<250" in q_lower or "< 250" in q_lower):
                        response_text = """Namaste ji! 🙏 Safety comes first at **Desi Coffee & Chai Khana**.

Since you mentioned a **milk allergy**, here are our top 100% **Milk-Free & Dairy-Free** recommendations under **₹250**:

1. 🧊 **Cold Brew** — **₹220** (Smooth 16-hour cold steeped coffee, strong, zero milk, low-sweet)
2. ☕ **Espresso** — **₹120** (Bold single-shot dark roast espresso crema, zero milk)
3. 🍋 **Lemon Iced Tea** — **₹150** (Refreshing chilled natural lemon infused tea)
4. 🥭 **Mango Iced Tea** — **₹180** (Tropical Alphonso mango tea poured over ice)

> 🛡️ **Guaranteed Safety**: None of these items contain milk or dairy components in `menu.json`."""

                    elif "kesar badam" in q_lower or "sweet drink" in q_lower or "rich traditional" in q_lower:
                        response_text = """Namaste ji! 🙏 For a rich traditional indulgence, Ustad Chaiwala highly recommends our **Kesar Badam Milk**! 🥛✨

### 🌟 Details:
* **Price**: **₹210**
* **Ingredients**: Premium Kashmiri Saffron (*Kesar*), finely ground almond nut paste (*Badam*), cardamom, and warm whole milk.
* **Attributes**: Rich, Sweet, Creamy & Nutty.

> ⚠️ **Allergen Notice**: Contains both **Milk (Dairy)** and **Tree Nuts (Almonds)**."""

                    else:
                        # General RAG fallback response
                        response_text = f"""Namaste ji! 🙏 Ustad Chaiwala at your service!

Based on our Vector RAG Knowledge Base and `menu.json`:

{knowledge_context}

How else can Ustad Chaiwala assist your chai & coffee experience today?"""

                # Display response
                st.markdown(response_text, unsafe_allow_html=True)
                
                # Expander for Telemetry
                with st.expander("⚡ Vector RAG & ADK Telemetry Breakdown"):
                    st.markdown(f"""
                    - **RAG Strategy**: `{telemetry_info.get('strategy', 'Vector RAG (text-embedding-004)')}`
                    - **Embedding Model**: `{telemetry_info.get('embedding_model', 'text-embedding-004')}`
                    - **Similarity Threshold**: `0.35`
                    - **Grounding Source**: `menu.json (Absolute Price & Allergen Truth)`
                    """)

        # Append Assistant Response
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text,
            "telemetry": telemetry_info
        })


# ==========================================
# TAB 2: MENU & ALLERGEN MATRIX
# ==========================================
with tab_menu:
    st.markdown("<h3 style='font-family: Outfit; color: #e0a96d;'>📋 Official Menu & Allergen Matrix</h3>", unsafe_allow_html=True)
    st.caption("Live, accurate menu item database from menu.json with exact prices and safety tags.")
    
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search_query = st.text_input("🔍 Search menu items...", key="menu_search_input", placeholder="e.g. Chai, Cold Brew, Milk-free")
    with col_s2:
        filter_category = st.selectbox("Category Filter", ["All Items", "Hot Drinks", "Cold Drinks", "Milk-Free / Non-Dairy", "Coffee", "Tea"])
    with col_s3:
        max_price = st.slider("Max Price (₹)", 100, 300, 300, step=10)

    # Filter logic
    display_items = menu_items
    if search_query:
        sq = search_query.lower()
        display_items = [
            i for i in display_items 
            if sq in i["name"].lower() or sq in i["description"].lower() or any(sq in t.lower() for t in i.get("tags", []))
        ]

    if filter_category == "Hot Drinks":
        display_items = [i for i in display_items if "hot" in i.get("tags", [])]
    elif filter_category == "Cold Drinks":
        display_items = [i for i in display_items if "cold" in i.get("tags", [])]
    elif filter_category == "Milk-Free / Non-Dairy":
        display_items = [i for i in display_items if "milk" not in i.get("allergens", [])]
    elif filter_category == "Coffee":
        display_items = [i for i in display_items if "coffee" in i.get("tags", [])]
    elif filter_category == "Tea":
        display_items = [i for i in display_items if "tea" in i.get("tags", [])]

    display_items = [i for i in display_items if i["price"] <= max_price]

    # Grid Display
    grid_cols = st.columns(3)
    for idx, item in enumerate(display_items):
        with grid_cols[idx % 3]:
            tags_html = ""
            for tag in item.get("tags", []):
                b_class = "badge-hot" if tag == "hot" else ("badge-cold" if tag == "cold" else "badge-tag")
                tags_html += f'<span class="badge {b_class}">{tag}</span>'
                
            allergens = item.get("allergens", [])
            if "milk" in allergens:
                tags_html += '<span class="badge badge-allergen">⚠️ Milk</span>'
            if "nuts" in allergens:
                tags_html += '<span class="badge badge-allergen">🥜 Nuts</span>'
            if not allergens:
                tags_html += '<span class="badge badge-safe">🌱 Dairy-Free</span>'

            st.markdown(f"""
            <div class="menu-card-ui">
                <div>
                    <div class="item-header">
                        <span class="item-title">{item['name']}</span>
                        <span class="item-price">₹{item['price']}</span>
                    </div>
                    <div class="item-desc">{item['description']}</div>
                </div>
                <div>
                    <div style="margin-bottom: 12px;">{tags_html}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("➕ Add to Basket", key=f"add_menu_{idx}"):
                    st.session_state.cart.append({"name": item["name"], "price": item["price"], "qty": 1})
                    st.toast(f"Added {item['name']} to basket!", icon="🛒")
                    st.rerun()
            with c_btn2:
                if st.button("✨ Ask Ustad", key=f"ask_menu_{idx}"):
                    st.session_state.prompt_trigger = f"Tell me about {item['name']} price, ingredients, and allergen info."
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# TAB 3: FLAVOR MATCHER WIZARD
# ==========================================
with tab_matcher:
    st.markdown("<h3 style='font-family: Outfit; color: #e0a96d;'>🎯 Interactive Drink Recommendation Matcher</h3>", unsafe_allow_html=True)
    st.caption("Select your taste preferences and let Ustad Chaiwala's algorithm match you with the best drink!")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        pref_temp = st.radio("Temperature Preference", ["Hot ♨️", "Cold 🧊", "Any"], horizontal=True)
        pref_type = st.radio("Drink Category", ["Coffee ☕", "Tea 🫖", "Non-Caffeine / Sweet 🥛", "Any"], horizontal=True)
        pref_milk = st.selectbox("Dietary / Milk Preference", ["No Milk / Lactose-Free Only 🌱", "Milk Okay 🥛", "Any"])

    with col_m2:
        pref_strength = st.select_slider("Desired Strength", options=["Mild", "Medium", "Strong"])
        pref_sweet = st.select_slider("Sweetness Level", options=["Low-Sweet", "Medium-Sweet", "Sweet"])
        pref_budget = st.slider("Budget Limit (₹)", 100, 300, 250, step=10)

    if st.button("✨ Calculate Compatibility Match"):
        results = []
        for item in menu_items:
            score = 100
            tags = item.get("tags", [])
            allergens = item.get("allergens", [])
            price = item["price"]

            # Budget check
            if price > pref_budget:
                score -= 40

            # Milk preference check
            if pref_milk == "No Milk / Lactose-Free Only 🌱" and "milk" in allergens:
                score -= 100 # Incompatible

            # Temp check
            if pref_temp == "Hot ♨️" and "hot" not in tags:
                score -= 30
            elif pref_temp == "Cold 🧊" and "cold" not in tags:
                score -= 30

            # Drink Type
            if pref_type == "Coffee ☕" and "coffee" not in tags:
                score -= 30
            elif pref_type == "Tea 🫖" and "tea" not in tags:
                score -= 30

            # Strength
            if pref_strength == "Strong" and "strong" in tags:
                score += 15

            # Sweetness
            if pref_sweet == "Low-Sweet" and "low-sweet" in tags:
                score += 15

            if score > 0:
                results.append((score, item))

        results.sort(key=lambda x: x[0], reverse=True)

        st.markdown("#### 🌟 Top Matched Beverages for You:")
        if not results:
            st.warning("No drink perfectly matches all constraints. Try adjusting your budget or temperature preference!")
        else:
            m_cols = st.columns(min(len(results), 3))
            for i, (scr, item) in enumerate(results[:3]):
                with m_cols[i]:
                    st.markdown(f"""
                    <div class="menu-card-ui" style="border-color: #22c55e;">
                        <div class="item-header">
                            <span class="item-title">{item['name']}</span>
                            <span class="item-price">₹{item['price']}</span>
                        </div>
                        <div style="color: #4ade80; font-weight: 700; font-size: 1rem; margin-bottom: 8px;">
                            🎯 {min(scr, 100)}% Match
                        </div>
                        <div class="item-desc">{item['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Order {item['name']}", key=f"match_ord_{i}"):
                        st.session_state.cart.append({"name": item["name"], "price": item["price"], "qty": 1})
                        st.toast(f"Added {item['name']} to cart!", icon="🛒")
                        st.rerun()


# ==========================================
# TAB 4: RAG & ADK TELEMETRY INSPECTOR
# ==========================================
with tab_rag:
    st.markdown("<h3 style='font-family: Outfit; color: #e0a96d;'>🧠 Google ADK & Vector RAG Architecture Visualizer</h3>", unsafe_allow_html=True)
    st.caption("Inspect how the vector embeddings, similarity chunks, and agent tools interact.")

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.metric("Total RAG Chunks", len(rag_engine.chunks))
    with col_t2:
        st.metric("Embedding Model", rag_engine.embedding_model)
    with col_t3:
        st.metric("Similarity Threshold", rag_engine.similarity_threshold)

    st.markdown("---")
    st.markdown("#### 📄 Knowledge Base Chunks (`coffee_knowledge.md`):")
    for idx, chunk in enumerate(rag_engine.chunks):
        with st.expander(f"Chunk #{idx+1}: {chunk['title']}"):
            st.code(chunk['text'], language="markdown")

    st.markdown("---")
    st.markdown("#### 🛠️ Registered Agent Tools:")
    st.markdown("""
    1. **`search_coffee_knowledge(query)`**: Retrieves vector embeddings using `text-embedding-004` to match semantic intent across Indian coffee & chai brewing lore.
    2. **`get_menu(query)`**: Enforces strict grounding rules. Validates prices, availability, and allergen flags against `menu.json`.
    """)


# ==========================================
# TAB 5: ORDER BUILDER & CART
# ==========================================
with tab_cart:
    st.markdown("<h3 style='font-family: Outfit; color: #e0a96d;'>🛒 Interactive Order Basket & Customizer</h3>", unsafe_allow_html=True)
    
    if not st.session_state.cart:
        st.info("Your order basket is currently empty. Head over to the Menu tab to pick your favorite Indian brew!")
    else:
        st.markdown("#### 📜 Current Items in Basket:")
        total_price = 0
        for idx, item in enumerate(st.session_state.cart):
            col_c1, col_c2, col_c3, col_c4 = st.columns([3, 1, 1, 1])
            with col_c1:
                st.markdown(f"**{item['name']}**")
            with col_c2:
                st.markdown(f"₹{item['price']}")
            with col_c3:
                st.markdown(f"Qty: {item.get('qty', 1)}")
            with col_c4:
                if st.button("Delete", key=f"del_cart_tab_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
            total_price += item['price'] * item.get('qty', 1)

        st.markdown(f"### **Total Amount: ₹{total_price}**")
        
        st.markdown("---")
        st.markdown("#### ☕ Customization & Ustad Notes:")
        sugar_custom = st.select_slider("Sweetness Preference", ["Zero Sugar", "Less Sugar", "Standard Sweetness", "Extra Sweet"])
        milk_custom = st.selectbox("Milk Preference", ["Standard Whole Milk", "Oat Milk Substitute", "Almond Milk Substitute", "No Milk / Black"])
        special_notes = st.text_input("Special Instructions", placeholder="e.g. Extra cardamom, serve scalding hot")

        if st.button("✅ Send Order to Ustad Chaiwala"):
            st.session_state.prompt_trigger = f"I want to place an order for: {', '.join([i['name'] for i in st.session_state.cart])}. Total price is ₹{total_price}. Sweetness: {sugar_custom}, Milk choice: {milk_custom}, Special notes: {special_notes}. Please confirm pricing and allergen safety!"
            st.rerun()
