"""
Metrics storage and aggregation for compression and performance tracking.
"""

from datetime import datetime
from typing import Dict, List, Optional
from src.database import get_connection


def store_chat_metric(
    query: str,
    category: Optional[str],
    retrieved_chunks: int,
    runtime_original_tokens: int,
    runtime_compressed_tokens: int,
    scaledown_latency_ms: float,
    gemini_latency_ms: float,
    was_resolved: Optional[bool] = None,
    created_ticket_id: Optional[int] = None
):
    """Store metrics for a chat interaction."""
    conn = get_connection()
    cursor = conn.cursor()
    
    compression_ratio = runtime_original_tokens / max(runtime_compressed_tokens, 1)
    total_latency_ms = scaledown_latency_ms + gemini_latency_ms
    
    cursor.execute("""
        INSERT INTO chat_metrics (
            query, category, retrieved_chunks,
            runtime_original_tokens, runtime_compressed_tokens, runtime_compression_ratio,
            scaledown_latency_ms, gemini_latency_ms, total_latency_ms,
            was_resolved, created_ticket_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        query, category, retrieved_chunks,
        runtime_original_tokens, runtime_compressed_tokens, compression_ratio,
        scaledown_latency_ms, gemini_latency_ms, total_latency_ms,
        was_resolved, created_ticket_id
    ))
    
    conn.commit()
    conn.close()


def store_compression_event(
    event_type: str,
    source_type: str,
    original_tokens: int,
    compressed_tokens: int,
    latency_ms: float
):
    """Store compression event for audit log."""
    conn = get_connection()
    cursor = conn.cursor()
    
    compression_ratio = original_tokens / max(compressed_tokens, 1)
    
    cursor.execute("""
        INSERT INTO compression_events (
            event_type, source_type, original_tokens, compressed_tokens,
            compression_ratio, latency_ms
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (event_type, source_type, original_tokens, compressed_tokens, compression_ratio, latency_ms))
    
    conn.commit()
    conn.close()


def get_aggregate_metrics() -> Dict:
    """Get aggregate metrics for dashboard."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Chat metrics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_chats,
            AVG(runtime_compression_ratio) as avg_compression_ratio,
            SUM(runtime_original_tokens - runtime_compressed_tokens) as total_tokens_saved,
            AVG(total_latency_ms) as avg_latency_ms,
            SUM(CASE WHEN was_resolved = 1 THEN 1 ELSE 0 END) as resolved_count,
            SUM(CASE WHEN created_ticket_id IS NOT NULL THEN 1 ELSE 0 END) as ticket_count
        FROM chat_metrics
    """)
    chat_stats = dict(cursor.fetchone())
    
    # Auto-resolution rate
    total_chats = chat_stats['total_chats'] or 0
    resolved_count = chat_stats['resolved_count'] or 0
    auto_resolution_rate = (resolved_count / total_chats * 100) if total_chats > 0 else 0
    
    # Top categories
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM chat_metrics
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
        LIMIT 5
    """)
    top_categories = [dict(row) for row in cursor.fetchall()]
    
    # KB compression stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total_chunks,
            AVG(original_tokens) as avg_original_tokens,
            AVG(compressed_tokens) as avg_compressed_tokens,
            AVG(CAST(original_tokens AS FLOAT) / CAST(compressed_tokens AS FLOAT)) as avg_kb_compression_ratio
        FROM kb_chunks
    """)
    kb_stats = dict(cursor.fetchone())
    
    # Time savings calculation
    # Baseline: 4 hours (240 minutes) for human support
    # Chatbot: 30 minutes average
    time_saved_per_resolution = 240 - 30  # 210 minutes
    total_time_saved_minutes = resolved_count * time_saved_per_resolution
    total_time_saved_hours = total_time_saved_minutes / 60
    
    conn.close()
    
    return {
        "total_chats": total_chats,
        "avg_compression_ratio": chat_stats['avg_compression_ratio'] or 0,
        "total_tokens_saved": chat_stats['total_tokens_saved'] or 0,
        "avg_latency_ms": chat_stats['avg_latency_ms'] or 0,
        "auto_resolution_rate": auto_resolution_rate,
        "resolved_count": resolved_count,
        "ticket_count": chat_stats['ticket_count'] or 0,
        "top_categories": top_categories,
        "kb_total_chunks": kb_stats['total_chunks'] or 0,
        "kb_avg_compression_ratio": kb_stats['avg_kb_compression_ratio'] or 0,
        "time_saved_hours": total_time_saved_hours,
        "time_saved_minutes": total_time_saved_minutes
    }


def get_chat_history() -> List[Dict]:
    """Get recent chat history with metrics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM chat_metrics
        ORDER BY created_at DESC
        LIMIT 100
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_compression_events() -> List[Dict]:
    """Get compression event history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM compression_events
        ORDER BY created_at DESC
        LIMIT 100
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


if __name__ == "__main__":
    from src.database import init_database
    init_database()
    
    # Test storing metrics
    store_chat_metric(
        query="How do I reset my password?",
        category="Authentication",
        retrieved_chunks=3,
        runtime_original_tokens=500,
        runtime_compressed_tokens=200,
        scaledown_latency_ms=150.5,
        gemini_latency_ms=300.2,
        was_resolved=True
    )
    
    # Get aggregate metrics
    metrics = get_aggregate_metrics()
    print(f"Metrics: {metrics}")
