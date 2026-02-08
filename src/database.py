"""
Database schema and initialization for IT Helpdesk Chatbot.
SQLite database with tables for KB chunks, tickets, and metrics.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

DB_PATH = "helpdesk.db"


def get_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # KB Chunks table - stores compressed knowledge base
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kb_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            text TEXT NOT NULL,
            compressed_text TEXT NOT NULL,
            raw_words INTEGER NOT NULL,
            compressed_words INTEGER NOT NULL,
            original_tokens INTEGER NOT NULL,
            compressed_tokens INTEGER NOT NULL,
            scaledown_latency_ms REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester_name TEXT DEFAULT 'Anonymous',
            department TEXT DEFAULT 'General',
            issue_summary TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Open',
            assignee TEXT DEFAULT 'Unassigned',
            tags TEXT DEFAULT '',
            from_chat_turn_id INTEGER NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP NULL,
            FOREIGN KEY (from_chat_turn_id) REFERENCES chat_metrics(id)
        )
    """)
    
    # Ticket notes table for internal notes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            created_by TEXT DEFAULT 'System',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    """)
    
    # Chat metrics table - per-turn compression metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            category TEXT,
            retrieved_chunks INTEGER NOT NULL,
            runtime_original_tokens INTEGER NOT NULL,
            runtime_compressed_tokens INTEGER NOT NULL,
            runtime_compression_ratio REAL NOT NULL,
            scaledown_latency_ms REAL NOT NULL,
            gemini_latency_ms REAL NOT NULL,
            total_latency_ms REAL NOT NULL,
            was_resolved BOOLEAN,
            created_ticket_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_ticket_id) REFERENCES tickets(id)
        )
    """)
    
    # Compression events table - audit log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compression_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            source_type TEXT NOT NULL,
            original_tokens INTEGER NOT NULL,
            compressed_tokens INTEGER NOT NULL,
            compression_ratio REAL NOT NULL,
            latency_ms REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")


def clear_kb():
    """Clear all KB chunks."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kb_chunks")
    conn.commit()
    conn.close()
    print("✅ KB chunks cleared")


if __name__ == "__main__":
    init_database()
