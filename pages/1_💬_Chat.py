"""
Chat Page - IT Helpdesk Chatbot
Grounded Q&A with ScaleDown compression and Gemini AI
"""

import streamlit as st
import time
from src.retriever import get_retriever
from src.scaledown_client import compress_text
from src.gemini_client import generate_answer
from src.metrics_store import store_chat_metric
from src.ticketing import create_ticket

st.set_page_config(page_title="Chat - IT Helpdesk", page_icon="💬", layout="wide")

st.title("💬 IT Helpdesk Chat")
st.markdown("Ask your IT questions and get instant answers from our knowledge base")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'last_sources' not in st.session_state:
    st.session_state.last_sources = []
if 'last_metrics' not in st.session_state:
    st.session_state.last_metrics = None

# Sidebar - Category filter
st.sidebar.markdown("### 🔍 Filters")
retriever = get_retriever()
categories = ["All"] + retriever.get_all_categories()
selected_category = st.sidebar.selectbox("Category", categories)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Tips")
st.sidebar.info("""
- Ask specific questions
- Include error messages if any
- Mention your device/OS
- Check sources for details
""")

# Chat interface
st.markdown("### Chat History")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Red flag keywords for urgent security issues
RED_FLAG_KEYWORDS = [
    "data breach", "ransomware", "account compromised", "phishing link clicked",
    "lost laptop", "unauthorized access", "malware", "virus detected",
    "hacked", "stolen device", "suspicious activity"
]

def detect_red_flag(query: str) -> bool:
    """Detect urgent security issues in query."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in RED_FLAG_KEYWORDS)

def get_confidence_score(chunks):
    """Get average confidence from retrieved chunks."""
    if not chunks:
        return 0.0
    return sum(chunk['score'] for chunk in chunks) / len(chunks)

def get_total_characters(chunks):
    """Get total character count from chunks."""
    return sum(len(chunk['compressed_text']) for chunk in chunks)

# User input
if prompt := st.chat_input("Ask your IT question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check for red flags
    is_red_flag = detect_red_flag(prompt)
    
    # Process query
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching knowledge base..."):
            # Retrieve relevant chunks
            category_filter = None if selected_category == "All" else selected_category
            retrieved_chunks = retriever.retrieve(prompt, top_k=3, category=category_filter)
            
            # Calculate confidence and character count
            confidence = get_confidence_score(retrieved_chunks)
            total_chars = get_total_characters(retrieved_chunks)
            
            # Check if red flag detected
            if is_red_flag:
                response = "🚨 **SECURITY ALERT DETECTED**\n\n"
                response += "Your query indicates a potential security incident. This requires immediate attention from our security team.\n\n"
                response += "**Immediate Actions:**\n"
                response += "1. Do NOT click any suspicious links\n"
                response += "2. Do NOT provide passwords or sensitive information\n"
                response += "3. Disconnect from network if you suspect compromise\n"
                response += "4. Contact IT Security immediately: ext. 9999\n\n"
                response += "I'm creating a HIGH PRIORITY security ticket for you now."
                
                st.error(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.last_sources = []
                st.session_state.last_metrics = None
                
                # Auto-create HIGH priority ticket
                ticket_id = create_ticket(
                    issue_summary=f"🚨 SECURITY: {prompt[:100]}",
                    description=f"**SECURITY INCIDENT REPORTED**\n\nUser Query: {prompt}\n\nDetected Keywords: Security red flag\n\nImmediate action required.",
                    category="Security",
                    priority="Critical",
                    tags="security,urgent,red-flag"
                )
                
                st.error(f"🎫 **Security Ticket #{ticket_id} Created** - Priority: CRITICAL")
                st.info("A security specialist will contact you immediately.")
                
                # Store metric
                store_chat_metric(
                    query=prompt,
                    category="Security",
                    retrieved_chunks=0,
                    runtime_original_tokens=0,
                    runtime_compressed_tokens=0,
                    scaledown_latency_ms=0,
                    gemini_latency_ms=0,
                    was_resolved=False,
                    created_ticket_id=ticket_id
                )
                
                st.session_state.show_ticket_form = False
                
            # Check confidence threshold and character count
            elif not retrieved_chunks or confidence < 0.20 or total_chars < 400:
                response = "I don't have enough verified information in our internal KB to answer this question safely.\n\n"
                response += f"**Retrieval Confidence:** {confidence:.2%} (minimum required: 20%)\n"
                response += f"**KB Content Found:** {total_chars} characters (minimum required: 400)\n\n"
                response += "To ensure you get accurate help, I recommend creating a support ticket. Please provide:\n"
                response += "- Device type (laptop/desktop/mobile)\n"
                response += "- Operating system (Windows/Mac/Linux)\n"
                response += "- Any error messages you're seeing"
                
                st.warning(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.last_sources = retrieved_chunks if retrieved_chunks else []
                st.session_state.last_metrics = {
                    'retrieved_chunks': len(retrieved_chunks) if retrieved_chunks else 0,
                    'confidence': confidence,
                    'total_chars': total_chars,
                    'escalated': True
                }
                
                # Auto-open ticket draft
                st.session_state.show_ticket_form = True
                
                # Build sources context
                sources_text = ""
                if retrieved_chunks:
                    sources_text = "\n\n**Retrieved KB Sources:**\n"
                    for i, chunk in enumerate(retrieved_chunks, 1):
                        sources_text += f"{i}. {chunk['title']} (Category: {chunk['category']})\n"
                
                st.session_state.ticket_draft = {
                    'issue_summary': prompt[:100],
                    'description': f"""**User Query:** {prompt}

**Retrieval Analysis:**
- Confidence Score: {confidence:.2%} (threshold: 20%)
- KB Content Found: {total_chars} characters (threshold: 400)
- Retrieved Chunks: {len(retrieved_chunks) if retrieved_chunks else 0}
{sources_text}

**Additional Information Needed:**
- Device type (laptop/desktop/mobile):
- Operating system (Windows/Mac/Linux):
- Error messages or screenshots:
- When did this issue start:""",
                    'tags': 'low-confidence,escalated'
                }
                
            else:
                # Combine retrieved context
                context = "\n\n---\n\n".join([
                    f"**{chunk['title']}** (Category: {chunk['category']})\n{chunk['compressed_text']}"
                    for chunk in retrieved_chunks
                ])
                
                # Runtime compression
                with st.spinner("🗜️ Compressing context..."):
                    compression_result = compress_text(context)
                    compressed_context = compression_result['compressed_text']
                
                # Generate answer
                with st.spinner("🧠 Generating answer..."):
                    answer_result = generate_answer(prompt, compressed_context)
                    answer = answer_result['answer']
                
                # Check if escalation needed
                if "INSUFFICIENT" in answer or "ESCALATE" in answer:
                    response = "I don't have enough verified information in our internal KB to answer this question safely. I recommend creating a support ticket for personalized assistance."
                    st.warning(response)
                    was_resolved = False
                    st.session_state.show_ticket_form = True
                else:
                    response = answer
                    st.markdown(response)
                    was_resolved = None  # User will indicate
                
                # Show compact ScaleDown metrics line
                tokens_saved = compression_result['original_tokens'] - compression_result['compressed_tokens']
                reduction_pct = (tokens_saved / compression_result['original_tokens'] * 100) if compression_result['original_tokens'] > 0 else 0
                
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 8px 12px; border-radius: 5px; margin-top: 10px; font-size: 0.9em;">
                    ⚡ <strong>ScaleDown:</strong> {compression_result['original_tokens']} → {compression_result['compressed_tokens']} tokens 
                    ({reduction_pct:.1f}% saved), latency {compression_result['latency_ms']:.0f} ms
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.last_sources = retrieved_chunks
                
                # Store metrics
                total_latency = compression_result['latency_ms'] + answer_result['latency_ms']
                metrics = {
                    'retrieved_chunks': len(retrieved_chunks),
                    'confidence': confidence,
                    'total_chars': total_chars,
                    'original_tokens': compression_result['original_tokens'],
                    'compressed_tokens': compression_result['compressed_tokens'],
                    'compression_ratio': compression_result['compression_ratio'],
                    'scaledown_latency_ms': compression_result['latency_ms'],
                    'gemini_latency_ms': answer_result['latency_ms'],
                    'total_latency_ms': total_latency
                }
                st.session_state.last_metrics = metrics
                
                store_chat_metric(
                    query=prompt,
                    category=category_filter,
                    retrieved_chunks=len(retrieved_chunks),
                    runtime_original_tokens=compression_result['original_tokens'],
                    runtime_compressed_tokens=compression_result['compressed_tokens'],
                    scaledown_latency_ms=compression_result['latency_ms'],
                    gemini_latency_ms=answer_result['latency_ms'],
                    was_resolved=was_resolved
                )

# Action buttons and sources (only show if there are messages)
if st.session_state.messages:
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Solved", use_container_width=True):
            st.success("Great! Glad I could help!")
            # Update last metric as resolved
            if len(st.session_state.messages) >= 2:
                from src.database import get_connection
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE chat_metrics 
                    SET was_resolved = 1 
                    WHERE id = (SELECT MAX(id) FROM chat_metrics)
                """)
                conn.commit()
                conn.close()
    
    with col2:
        if st.button("❌ Not Solved", use_container_width=True):
            st.info("Let me create a support ticket for you.")
            # Update metric as not resolved
            from src.database import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE chat_metrics 
                SET was_resolved = 0 
                WHERE id = (SELECT MAX(id) FROM chat_metrics)
            """)
            conn.commit()
            conn.close()
    
    with col3:
        if st.button("🎫 Create Ticket", use_container_width=True):
            st.session_state.show_ticket_form = True

# Ticket creation form
if 'show_ticket_form' in st.session_state and st.session_state.show_ticket_form:
    st.markdown("### 🎫 Create Support Ticket")
    
    # Get draft data if available
    draft = st.session_state.get('ticket_draft', {})
    default_summary = draft.get('issue_summary', st.session_state.messages[-2]['content'][:100] if len(st.session_state.messages) >= 2 else "")
    default_description = draft.get('description', "Issue from chat:\n\n" + "\n\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-4:]]))
    default_tags = draft.get('tags', '')
    
    with st.form("ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            requester_name = st.text_input("Your Name *", value="Anonymous")
        with col2:
            department = st.text_input("Department", value="General")
        
        issue_summary = st.text_input("Issue Summary *", value=default_summary, max_chars=200)
        description = st.text_area("Detailed Description *", value=default_description, height=250)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category = st.selectbox("Category *", ["Network", "Authentication", "Email", "Hardware", "Software", "Performance", "File Sharing", "Security", "Other"])
        with col2:
            priority = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"])
        with col3:
            assignee = st.text_input("Assign To", value="Unassigned")
        
        tags = st.text_input("Tags (comma-separated)", value=default_tags, placeholder="e.g., urgent, vpn, windows")
        
        submitted = st.form_submit_button("Create Ticket", type="primary")
        
        if submitted:
            if not issue_summary or not description:
                st.error("Please fill in all required fields (*)")
            else:
                # Get the last chat metric ID if this is from chat
                from_chat_turn_id = None
                if len(st.session_state.messages) > 0:
                    from src.database import get_connection
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT MAX(id) as max_id FROM chat_metrics")
                    result = cursor.fetchone()
                    from_chat_turn_id = result['max_id'] if result and result['max_id'] else None
                    conn.close()
                
                ticket_id = create_ticket(
                    issue_summary=issue_summary,
                    description=description,
                    category=category,
                    priority=priority,
                    requester_name=requester_name,
                    department=department,
                    assignee=assignee,
                    tags=tags,
                    from_chat_turn_id=from_chat_turn_id
                )
                st.success(f"✅ Ticket #{ticket_id} created successfully!")
                
                # Update metric with ticket ID if applicable
                if from_chat_turn_id:
                    from src.database import get_connection
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE chat_metrics 
                        SET created_ticket_id = ? 
                        WHERE id = ?
                    """, (ticket_id, from_chat_turn_id))
                    conn.commit()
                    conn.close()
                
                st.session_state.show_ticket_form = False
                if 'ticket_draft' in st.session_state:
                    del st.session_state.ticket_draft
                st.rerun()

# Sources expander
if st.session_state.last_sources:
    with st.expander("📚 View Sources", expanded=False):
        st.markdown("### Retrieved Knowledge Base Chunks")
        for i, source in enumerate(st.session_state.last_sources):
            st.markdown(f"**{i+1}. {source['title']}** (Category: {source['category']}, Relevance: {source['score']:.3f})")
            st.markdown(f"```\n{source['text'][:300]}...\n```")
            st.markdown("---")

# Metrics expander
if st.session_state.last_metrics:
    with st.expander("📊 Retrieval & Compression Metrics", expanded=False):
        m = st.session_state.last_metrics
        
        # Show confidence and character count if available
        if 'confidence' in m:
            col1, col2, col3 = st.columns(3)
            col1.metric("Retrieval Confidence", f"{m['confidence']:.2%}", 
                       help="TF-IDF cosine similarity score (threshold: 20%)")
            col2.metric("KB Content Found", f"{m.get('total_chars', 0)} chars",
                       help="Total characters in retrieved snippets (threshold: 400)")
            col3.metric("Retrieved Chunks", m['retrieved_chunks'])
        
        # Show compression metrics if not escalated
        if not m.get('escalated', False):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Compression Ratio", f"{m.get('compression_ratio', 0):.2f}x")
            col2.metric("Tokens Saved", m.get('original_tokens', 0) - m.get('compressed_tokens', 0))
            col3.metric("Total Latency", f"{m.get('total_latency_ms', 0):.0f}ms")
            
            st.markdown(f"""
            - **Original Tokens**: {m.get('original_tokens', 0)}
            - **Compressed Tokens**: {m.get('compressed_tokens', 0)}
            - **ScaleDown Latency**: {m.get('scaledown_latency_ms', 0):.2f}ms
            - **Gemini Latency**: {m.get('gemini_latency_ms', 0):.2f}ms
            """)
        else:
            st.info("Query escalated due to insufficient KB coverage.")
