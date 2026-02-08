"""
Ticketing system with CRUD operations.
Mock adapter for Jira/ServiceNow integration.
"""

from datetime import datetime
from typing import List, Dict, Optional
from src.database import get_connection


def create_ticket(
    issue_summary: str,
    description: str,
    category: str,
    priority: str = "Medium",
    requester_name: str = "Anonymous",
    department: str = "General",
    assignee: str = "Unassigned",
    tags: str = "",
    from_chat_turn_id: Optional[int] = None
) -> int:
    """Create a new ticket."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO tickets (
            requester_name, department, issue_summary, description, 
            category, priority, status, assignee, tags, from_chat_turn_id
        )
        VALUES (?, ?, ?, ?, ?, ?, 'Open', ?, ?, ?)
    """, (requester_name, department, issue_summary, description, category, priority, assignee, tags, from_chat_turn_id))
    
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # TODO: Mock Jira/ServiceNow integration
    # _sync_to_jira(ticket_id, issue_summary, description, category, priority)
    
    return ticket_id


def get_ticket(ticket_id: int) -> Optional[Dict]:
    """Get ticket by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def list_tickets(
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict]:
    """List tickets with optional filters."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    
    if search:
        query += " AND (issue_summary LIKE ? OR description LIKE ? OR requester_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_ticket_status(ticket_id: int, status: str) -> bool:
    """Update ticket status."""
    conn = get_connection()
    cursor = conn.cursor()
    
    resolved_at = None
    if status in ["Resolved", "Closed"]:
        resolved_at = datetime.now().isoformat()
    
    cursor.execute("""
        UPDATE tickets 
        SET status = ?, updated_at = CURRENT_TIMESTAMP, resolved_at = ?
        WHERE id = ?
    """, (status, resolved_at, ticket_id))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    # TODO: Mock Jira/ServiceNow sync
    # if success:
    #     _sync_status_to_jira(ticket_id, status)
    
    return success


def update_ticket_priority(ticket_id: int, priority: str) -> bool:
    """Update ticket priority."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE tickets 
        SET priority = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (priority, ticket_id))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success


def update_ticket_assignee(ticket_id: int, assignee: str) -> bool:
    """Update ticket assignee."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE tickets 
        SET assignee = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (assignee, ticket_id))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success


def add_ticket_note(ticket_id: int, note: str, created_by: str = "System") -> int:
    """Add internal note to ticket."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO ticket_notes (ticket_id, note, created_by)
        VALUES (?, ?, ?)
    """, (ticket_id, note, created_by))
    
    note_id = cursor.lastrowid
    
    # Update ticket updated_at
    cursor.execute("""
        UPDATE tickets 
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (ticket_id,))
    
    conn.commit()
    conn.close()
    
    return note_id


def get_ticket_notes(ticket_id: int) -> List[Dict]:
    """Get all notes for a ticket."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM ticket_notes 
        WHERE ticket_id = ? 
        ORDER BY created_at DESC
    """, (ticket_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_ticket_stats() -> Dict:
    """Get ticket statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM tickets")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as open FROM tickets WHERE status = 'Open'")
    open_count = cursor.fetchone()['open']
    
    cursor.execute("SELECT COUNT(*) as resolved FROM tickets WHERE status IN ('Resolved', 'Closed')")
    resolved = cursor.fetchone()['resolved']
    
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM tickets 
        GROUP BY category 
        ORDER BY count DESC 
        LIMIT 5
    """)
    top_categories = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total": total,
        "open": open_count,
        "resolved": resolved,
        "top_categories": top_categories
    }


# Mock Jira/ServiceNow adapter stubs
def _sync_to_jira(ticket_id: int, issue_summary: str, description: str, category: str, priority: str):
    """TODO: Implement Jira API integration."""
    pass


def _sync_status_to_jira(ticket_id: int, status: str):
    """TODO: Implement Jira status sync."""
    pass


if __name__ == "__main__":
    from src.database import init_database
    init_database()
    
    # Test ticket creation
    ticket_id = create_ticket(
        issue_summary="VPN not connecting",
        description="Cannot connect to VPN from home",
        category="Network",
        priority="High",
        requester_name="John Doe",
        department="Engineering"
    )
    print(f"Created ticket #{ticket_id}")
    
    # Test adding note
    note_id = add_ticket_note(ticket_id, "Investigating VPN server logs", "IT Support")
    print(f"Added note #{note_id}")
    
    # Test listing
    tickets = list_tickets()
    print(f"Total tickets: {len(tickets)}")
    
    # Test stats
    stats = get_ticket_stats()
    print(f"Stats: {stats}")
