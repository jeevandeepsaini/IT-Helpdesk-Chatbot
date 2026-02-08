"""
Admin/KB Page - IT Helpdesk Chatbot
Manage knowledge base and upload documents
"""

import streamlit as st
import plotly.express as px
from src.kb_pipeline import rebuild_kb_index, get_kb_stats
from src.database import get_connection

st.set_page_config(page_title="Admin/KB - IT Helpdesk", page_icon="⚙️", layout="wide")

st.title("⚙️ Knowledge Base Administration")
st.markdown("Manage and update the knowledge base")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 KB Statistics", "📤 Upload & Rebuild", "🗑️ Manage KB"])

with tab1:
    st.markdown("### Knowledge Base Statistics")
    
    stats = get_kb_stats()
    
    if stats['total_chunks'] and stats['total_chunks'] > 0:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Chunks", stats['total_chunks'])
        col2.metric("Categories", stats['total_categories'])
        col3.metric("Total Tokens (Original)", f"{stats['total_original_tokens']:,}")
        col4.metric("Avg Compression Ratio", f"{stats['avg_compression_ratio']:.2f}x" if stats['avg_compression_ratio'] else "N/A")
        
        # Category breakdown
        if stats['categories']:
            st.markdown("### Category Breakdown")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                fig = px.pie(
                    values=[cat['count'] for cat in stats['categories']],
                    names=[cat['category'] for cat in stats['categories']],
                    title="Chunks by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Table
                st.markdown("**Category Details**")
                for cat in stats['categories']:
                    st.markdown(f"- **{cat['category']}**: {cat['count']} chunks")
    else:
        st.info("No KB content yet. Upload documents to get started!")

with tab2:
    st.markdown("### 📤 Upload Documents & Rebuild KB")
    
    st.markdown("""
    Upload new documents and tickets to rebuild the knowledge base. The system will:
    1. Save uploaded files to `data/uploads/`
    2. Compress each document using ScaleDown (model: gemini-2.5-flash, rate: auto)
    3. Store compressed chunks in `storage/kb_chunks.json`
    4. Build TF-IDF index and save to `storage/tfidf_vectorizer.pkl` and `storage/tfidf_matrix.pkl`
    """)
    
    st.markdown("---")
    
    # File uploaders
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 Upload Markdown/Text Files**")
        md_files = st.file_uploader(
            "Upload .md or .txt files",
            type=['md', 'txt'],
            accept_multiple_files=True,
            help="Upload multiple documentation files"
        )
        
        if md_files:
            st.success(f"✅ {len(md_files)} file(s) selected")
            for file in md_files:
                st.markdown(f"- {file.name}")
    
    with col2:
        st.markdown("**📊 Upload Resolved Tickets CSV**")
        csv_file = st.file_uploader(
            "Upload CSV file",
            type=['csv'],
            help="Upload resolved tickets CSV"
        )
        
        if csv_file:
            st.success(f"✅ {csv_file.name} selected")
    
    st.markdown("---")
    
    # Options
    include_existing = st.checkbox(
        "Include existing documents from data/docs/",
        value=True,
        help="Include documents already in data/docs/ directory"
    )
    
    # Rebuild button
    if st.button("🔨 Rebuild KB Index", type="primary", use_container_width=True):
        if not md_files and not csv_file and not include_existing:
            st.error("Please upload files or enable 'Include existing documents'")
        else:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current, total, message):
                progress = current / total if total > 0 else 0
                progress_bar.progress(progress)
                status_text.text(message)
            
            # Run rebuild
            with st.spinner("Rebuilding KB..."):
                result = rebuild_kb_index(
                    md_files=md_files,
                    csv_file=csv_file,
                    include_existing_docs=include_existing,
                    progress_callback=update_progress
                )
            
            # Show results
            if result['success']:
                st.success(f"✅ KB rebuilt successfully! {result['chunks_count']} chunks created.")
                
                if result['errors']:
                    st.warning("⚠️ Some warnings occurred:")
                    for error in result['errors']:
                        st.markdown(f"- {error}")
                
                # Show file status
                st.markdown("### 📁 Processing Summary")
                if md_files:
                    st.markdown(f"**Uploaded Documents:** {len(md_files)} files")
                if csv_file:
                    st.markdown(f"**Uploaded Tickets:** {csv_file.name}")
                if include_existing:
                    st.markdown("**Existing Documents:** Included from data/docs/")
                
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ KB rebuild failed: {result['error']}")
                
                if result['errors']:
                    st.markdown("**Errors:**")
                    for error in result['errors']:
                        st.markdown(f"- {error}")
                
                st.markdown("""
                **Troubleshooting:**
                - Check that your ScaleDown API key is configured correctly
                - Verify that the uploaded files are valid markdown/text/CSV
                - Check the console for detailed error messages
                """)

with tab3:
    st.markdown("### 🗑️ Manage Knowledge Base")
    
    st.warning("⚠️ **Caution**: These actions will modify the knowledge base")
    
    # Manual document entry
    with st.expander("➕ Add Document Manually"):
        with st.form("manual_doc_form"):
            doc_title = st.text_input("Document Title")
            doc_category = st.selectbox("Category", [
                "Network", "Authentication", "Email", "Hardware", 
                "Software", "Performance", "File Sharing", "Security", "Other"
            ])
            doc_content = st.text_area("Content (Markdown)", height=300)
            
            if st.form_submit_button("Add Document"):
                if doc_title and doc_content:
                    # Save to file
                    import os
                    os.makedirs("data/docs", exist_ok=True)
                    filename = doc_title.lower().replace(' ', '_') + '.md'
                    filepath = os.path.join("data/docs", filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"# {doc_title}\n\n{doc_content}")
                    
                    st.success(f"✅ Document saved to {filepath}")
                    st.info("Click 'Rebuild KB Index' in the Upload tab to include this document")
                else:
                    st.error("Please fill in all fields")
    
    # Clear KB
    with st.expander("🗑️ Clear Knowledge Base"):
        st.warning("This will delete all KB chunks from the database. Files will not be deleted.")
        
        if st.button("Clear KB", type="secondary"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kb_chunks")
            conn.commit()
            conn.close()
            
            st.success("✅ Knowledge base cleared")
            st.rerun()
    
    # View storage info
    with st.expander("� Storage Information"):
        import os
        
        st.markdown("**Storage Files:**")
        
        files_to_check = [
            ("storage/kb_chunks.json", "KB Chunks JSON"),
            ("storage/tfidf_vectorizer.pkl", "TF-IDF Vectorizer"),
            ("storage/tfidf_matrix.pkl", "TF-IDF Matrix"),
            ("helpdesk.db", "SQLite Database")
        ]
        
        for filepath, description in files_to_check:
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                size_kb = size / 1024
                st.markdown(f"- ✅ **{description}**: {filepath} ({size_kb:.2f} KB)")
            else:
                st.markdown(f"- ❌ **{description}**: Not found")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>💡 Tip: Rebuild the KB index after uploading new documents or tickets</small>
</div>
""", unsafe_allow_html=True)
