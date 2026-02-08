"""
IT Helpdesk Chatbot - Main Streamlit Application
Enterprise chatbot with ScaleDown compression and Gemini AI
"""

import streamlit as st
import os
from src.database import init_database
from src.kb_pipeline import rebuild_kb_index, get_kb_stats
from src.retriever import get_retriever

# Page configuration
st.set_page_config(
    page_title="IT Helpdesk Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
        color: #333;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def initialize_system():
    """Initialize database and KB index on first run."""
    # Initialize database
    if not os.path.exists("helpdesk.db"):
        with st.spinner("🔧 Initializing database..."):
            init_database()
            st.success("✅ Database initialized")
    
    # Build KB index if not exists
    if not os.path.exists("storage/kb_index.pkl"):
        with st.spinner("📚 Building knowledge base index from sample data..."):
            try:
                rebuild_kb_index()
                st.success("✅ Knowledge base index built successfully")
            except Exception as e:
                st.warning(f"⚠️ Could not build KB index: {e}")
                st.info("You can build the index manually from the Admin/KB page")
    
    # Load retriever
    try:
        retriever = get_retriever()
        if not retriever.loaded:
            retriever.load_index()
    except Exception as e:
        st.warning(f"⚠️ Could not load retriever: {e}")

# Initialize system
initialize_system()

# Sidebar title
st.sidebar.title("🤖 IT Helpdesk Chatbot")

# Main page content
st.markdown('<div class="main-header">🤖 IT Helpdesk Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Enterprise AI Assistant with ScaleDown Compression & Gemini AI</div>', unsafe_allow_html=True)

# Welcome message
st.markdown("""
Welcome to the **IT Helpdesk Chatbot MVP**! This intelligent assistant helps you resolve IT issues quickly using:
- 🗜️ **ScaleDown.ai** for knowledge base compression
- 🧠 **Gemini 2.5 Flash** for grounded answer generation
- 📊 **Real-time metrics** tracking compression and performance
- 🎫 **Integrated ticketing** for escalation
""")

# Check API keys
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔑 API Configuration")
    scaledown_key = os.getenv("SCALEDOWN_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if scaledown_key:
        st.success("✅ ScaleDown API key configured")
    else:
        st.error("❌ ScaleDown API key missing")
        st.info("Add SCALEDOWN_API_KEY to .env file")
    
    if gemini_key:
        st.success("✅ Gemini API key configured")
    else:
        st.error("❌ Gemini API key missing")
        st.info("Add GEMINI_API_KEY to .env file")

with col2:
    st.markdown("### 📊 Knowledge Base Status")
    try:
        stats = get_kb_stats()
        st.metric("Total KB Chunks", stats.get('total_chunks', 0))
        st.metric("Categories", stats.get('total_categories', 0))
        if stats.get('avg_compression_ratio'):
            st.metric("Avg Compression Ratio", f"{stats['avg_compression_ratio']:.2f}x")
    except Exception as e:
        st.warning("KB stats not available. Build index from Admin/KB page.")

# Features
st.markdown("### 🚀 Features")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h4>💬 Chat</h4>
        <p>Ask IT questions and get instant grounded answers from compressed KB</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h4>🎫 Tickets</h4>
        <p>Create and track support tickets with full lifecycle management</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h4>⚙️ Admin/KB</h4>
        <p>Upload docs, manage KB, rebuild compression index</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-box">
        <h4>📊 Metrics</h4>
        <p>View compression stats, token savings, and performance analytics</p>
    </div>
    """, unsafe_allow_html=True)

# Quick start guide
st.markdown("### 🎯 Quick Start")

st.markdown("""
1. **Set up API keys**: Copy `.env.example` to `.env` and add your API keys
2. **Chat**: Go to the 💬 Chat page to ask IT questions
3. **Create tickets**: Use 🎫 Tickets page to manage support requests
4. **View metrics**: Check 📊 Metrics page for compression and performance stats
5. **Manage KB**: Use ⚙️ Admin/KB page to upload new documentation

**Sample Questions to Try:**
- "How do I reset my password?"
- "VPN is not connecting, what should I do?"
- "How do I set up email on my phone?"
- "My computer is running slow, how can I fix it?"
""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Built with ❤️ using Streamlit, ScaleDown.ai, and Gemini 2.5 Flash<br>
    <small>Hackathon MVP - Enterprise IT Helpdesk Chatbot</small>
</div>
""", unsafe_allow_html=True)
