"""
Knowledge Base Pipeline
Handles loading, compressing, and indexing documents and tickets.
Supports multi-file upload and progress tracking.
"""

import os
import json
import csv
import pickle
from typing import List, Dict, Optional, Callable
from datetime import datetime
from src.scaledown_client import compress_text
from src.database import get_connection


def save_uploaded_files(md_files, csv_file) -> Dict:
    """Save uploaded files to data/uploads/ directory."""
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    saved_files = {"md_files": [], "csv_file": None}
    
    # Save markdown/text files
    if md_files:
        for uploaded_file in md_files:
            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files["md_files"].append(file_path)
    
    # Save CSV file
    if csv_file:
        file_path = os.path.join(upload_dir, csv_file.name)
        with open(file_path, "wb") as f:
            f.write(csv_file.getbuffer())
        saved_files["csv_file"] = file_path
    
    return saved_files


def load_documents_from_files(file_paths: List[str]) -> List[Dict]:
    """Load documents from specific file paths."""
    documents = []
    
    for filepath in file_paths:
        if filepath.endswith(('.md', '.txt')):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract title from filename
                filename = os.path.basename(filepath)
                title = filename.replace('.md', '').replace('.txt', '').replace('_', ' ').title()
                
                # Infer category from filename
                category = infer_category(filename.lower())
                
                documents.append({
                    'title': title,
                    'content': content,
                    'category': category,
                    'source': filename
                })
    
    return documents


def load_documents_from_directory(directory: str = "data/docs") -> List[Dict]:
    """Load all markdown documents from directory."""
    documents = []
    
    if not os.path.exists(directory):
        return documents
    
    for filename in os.listdir(directory):
        if filename.endswith(('.md', '.txt')):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract title from filename
                title = filename.replace('.md', '').replace('.txt', '').replace('_', ' ').title()
                
                # Infer category
                category = infer_category(filename.lower())
                
                documents.append({
                    'title': title,
                    'content': content,
                    'category': category,
                    'source': filename
                })
    
    return documents


def infer_category(filename: str) -> str:
    """Infer category from filename."""
    if "vpn" in filename or "network" in filename or "remote" in filename:
        return "Network"
    elif "password" in filename or "mfa" in filename or "auth" in filename:
        return "Authentication"
    elif "email" in filename:
        return "Email"
    elif "software" in filename or "installation" in filename:
        return "Software"
    elif "printer" in filename or "hardware" in filename:
        return "Hardware"
    elif "file" in filename or "sharing" in filename:
        return "File Sharing"
    elif "performance" in filename:
        return "Performance"
    elif "security" in filename:
        return "Security"
    else:
        return "General"


def load_tickets_from_csv(csv_path: str) -> List[Dict]:
    """Load resolved tickets from CSV."""
    tickets = []
    
    if not os.path.exists(csv_path):
        return tickets
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Handle different CSV formats
            title = row.get('title', row.get('issue', 'Untitled'))
            content = row.get('resolution', row.get('description', ''))
            category = row.get('category', 'Other')
            
            tickets.append({
                'title': title,
                'content': content,
                'category': category,
                'source': 'resolved_tickets.csv'
            })
    
    return tickets


def compress_and_store_documents(
    documents: List[Dict],
    progress_callback: Optional[Callable] = None
) -> tuple:
    """
    Compress documents using ScaleDown and store in database.
    Returns (chunks, errors).
    """
    chunks = []
    errors = []
    
    for i, doc in enumerate(documents):
        try:
            if progress_callback:
                progress_callback(i, len(documents), f"Compressing: {doc['title'][:40]}...")
            
            # Compress using ScaleDown with gemini-2.5-flash model and auto rate
            result = compress_text(
                doc['content'],
                target_model="gemini-2.5-flash"
            )
            
            if not result['success']:
                error_msg = f"Failed to compress '{doc['title']}': {result.get('error', 'Unknown error')}"
                errors.append(error_msg)
                # Stop on ScaleDown failure
                raise Exception(error_msg)
            
            # Create chunk
            chunk = {
                'title': doc['title'],
                'category': doc['category'],
                'source': doc['source'],
                'original_text': doc['content'],
                'compressed_text': result['compressed_text'],
                'original_tokens': result['original_tokens'],
                'compressed_tokens': result['compressed_tokens'],
                'original_words': result['original_words'],
                'compressed_words': result['compressed_words'],
                'compression_ratio': result['compression_ratio'],
                'latency_ms': result['latency_ms'],
                'created_at': datetime.now().isoformat()
            }
            
            chunks.append(chunk)
            
            # Store in database
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO kb_chunks (
                    source_id, title, category, text, compressed_text,
                    raw_words, compressed_words, original_tokens, compressed_tokens,
                    scaledown_latency_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc['source'], chunk['title'], chunk['category'],
                chunk['original_text'], chunk['compressed_text'],
                chunk['original_words'], chunk['compressed_words'],
                chunk['original_tokens'], chunk['compressed_tokens'],
                chunk['latency_ms']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            error_msg = f"Error processing '{doc['title']}': {str(e)}"
            errors.append(error_msg)
            # Stop on error
            raise Exception(error_msg)
    
    return chunks, errors


def save_chunks_to_json(chunks: List[Dict], filepath: str = "storage/kb_chunks.json"):
    """Save chunks to JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)


def build_tfidf_index(chunks: List[Dict]) -> tuple:
    """Build TF-IDF index from chunks."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    if not chunks:
        return None, None
    
    # Combine title and compressed text for indexing
    texts = [f"{chunk['title']} {chunk['compressed_text']}" for chunk in chunks]
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    # Fit and transform
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    return vectorizer, tfidf_matrix


def save_tfidf_index(vectorizer, tfidf_matrix):
    """Save TF-IDF index to disk."""
    os.makedirs("storage", exist_ok=True)
    
    with open("storage/tfidf_vectorizer.pkl", 'wb') as f:
        pickle.dump(vectorizer, f)
    
    with open("storage/tfidf_matrix.pkl", 'wb') as f:
        pickle.dump(tfidf_matrix, f)


def rebuild_kb_index(
    md_files=None,
    csv_file=None,
    include_existing_docs=True,
    progress_callback: Optional[Callable] = None
) -> Dict:
    """
    Rebuild entire KB index.
    
    Args:
        md_files: List of uploaded markdown/text files
        csv_file: Uploaded CSV file with resolved tickets
        include_existing_docs: Whether to include docs from data/docs/
        progress_callback: Function(current, total, message) to call with progress
    
    Returns:
        Dict with success, chunks_count, errors
    """
    all_documents = []
    errors = []
    
    try:
        # Save uploaded files
        if md_files or csv_file:
            if progress_callback:
                progress_callback(0, 100, "Saving uploaded files...")
            saved_files = save_uploaded_files(md_files, csv_file)
        else:
            saved_files = {"md_files": [], "csv_file": None}
        
        # Load documents from uploads
        if saved_files["md_files"]:
            if progress_callback:
                progress_callback(10, 100, "Loading uploaded documents...")
            uploaded_docs = load_documents_from_files(saved_files["md_files"])
            all_documents.extend(uploaded_docs)
        
        # Load documents from data/docs/
        if include_existing_docs:
            if progress_callback:
                progress_callback(20, 100, "Loading existing documents...")
            existing_docs = load_documents_from_directory("data/docs")
            all_documents.extend(existing_docs)
        
        # Load tickets from CSV
        csv_path = saved_files["csv_file"] if saved_files["csv_file"] else "data/resolved_tickets.csv"
        if os.path.exists(csv_path):
            if progress_callback:
                progress_callback(30, 100, "Loading tickets...")
            tickets = load_tickets_from_csv(csv_path)
            all_documents.extend(tickets)
        
        if not all_documents:
            return {
                "success": False,
                "error": "No documents found to process",
                "chunks_count": 0,
                "errors": []
            }
        
        # Clear existing KB
        if progress_callback:
            progress_callback(40, 100, "Clearing existing KB...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kb_chunks")
        conn.commit()
        conn.close()
        
        # Compress and store documents
        if progress_callback:
            progress_callback(50, 100, "Compressing documents...")
        
        def compress_progress(current, total, message):
            # Map compression progress to 50-80% range
            progress = 50 + int((current / total) * 30)
            if progress_callback:
                progress_callback(progress, 100, message)
        
        chunks, compress_errors = compress_and_store_documents(
            all_documents,
            progress_callback=compress_progress
        )
        errors.extend(compress_errors)
        
        if not chunks:
            return {
                "success": False,
                "error": "No chunks created. Check errors.",
                "chunks_count": 0,
                "errors": errors
            }
        
        # Save chunks to JSON
        if progress_callback:
            progress_callback(80, 100, "Saving chunks to JSON...")
        save_chunks_to_json(chunks, "storage/kb_chunks.json")
        
        # Build and save TF-IDF index
        if progress_callback:
            progress_callback(90, 100, "Building TF-IDF index...")
        vectorizer, tfidf_matrix = build_tfidf_index(chunks)
        
        if vectorizer and tfidf_matrix is not None:
            save_tfidf_index(vectorizer, tfidf_matrix)
        
        if progress_callback:
            progress_callback(100, 100, "Complete!")
        
        return {
            "success": True,
            "chunks_count": len(chunks),
            "errors": errors
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "chunks_count": 0,
            "errors": errors + [str(e)]
        }


def get_kb_stats() -> Dict:
    """Get KB statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_chunks,
            COUNT(DISTINCT category) as total_categories,
            SUM(original_tokens) as total_original_tokens,
            SUM(compressed_tokens) as total_compressed_tokens,
            AVG(CAST(original_tokens AS FLOAT) / CAST(compressed_tokens AS FLOAT)) as avg_compression_ratio
        FROM kb_chunks
    """)
    
    stats = dict(cursor.fetchone())
    
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM kb_chunks
        GROUP BY category
        ORDER BY count DESC
    """)
    
    categories = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    stats['categories'] = categories
    return stats


if __name__ == "__main__":
    from src.database import init_database
    init_database()
    
    # Test rebuild
    result = rebuild_kb_index()
    print(f"Result: {result}")
