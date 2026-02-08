"""
Tickets Page - IT Helpdesk Chatbot
Create, view, and manage support tickets
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.ticketing import (
    create_ticket, list_tickets, get_ticket, 
    update_ticket_status, update_ticket_priority, update_ticket_assignee,
    add_ticket_note, get_ticket_notes, get_ticket_stats
)

st.set_page_config(page_title="Tickets - IT Helpdesk", page_icon="🎫", layout="wide")

st.title("🎫 Support Tickets")
st.markdown("Create and manage IT support tickets")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Tickets", "➕ Create Ticket", "📊 Statistics"])

with tab1:
    st.markdown("### All Tickets")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox("Status", ["All", "Open", "In Progress", "Resolved", "Closed"])
    
    with col2:
        priority_filter = st.selectbox("Priority", ["All", "Low", "Medium", "High", "Critical"])
    
    with col3:
        category_filter = st.selectbox("Category", ["All", "Network", "Authentication", "Email", "Hardware", "Software", "Performance", "File Sharing", "Security", "Other"])
    
    with col4:
        search_query = st.text_input("🔍 Search", placeholder="Search tickets...")
    
    # Get tickets
    tickets = list_tickets(
        status=None if status_filter == "All" else status_filter,
        category=None if category_filter == "All" else category_filter,
        priority=None if priority_filter == "All" else priority_filter,
        search=search_query if search_query else None
    )
    
    if tickets:
        st.markdown(f"**Found {len(tickets)} ticket(s)**")
        
        # Display tickets
        for ticket in tickets:
            # Priority badge color
            priority_colors = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
            priority_badge = priority_colors.get(ticket['priority'], "⚪")
            
            with st.expander(f"{priority_badge} #{ticket['id']} - {ticket['issue_summary']} [{ticket['status']}]"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Requester:** {ticket['requester_name']} ({ticket['department']})")
                    st.markdown(f"**Assignee:** {ticket['assignee']}")
                    
                    st.markdown(f"**Description:**")
                    st.markdown(ticket['description'])
                    
                    st.markdown(f"**Category:** {ticket['category']} | **Priority:** {ticket['priority']}")
                    
                    if ticket['tags']:
                        st.markdown(f"**Tags:** {ticket['tags']}")
                    
                    st.markdown(f"**Created:** {ticket['created_at']}")
                    if ticket['resolved_at']:
                        st.markdown(f"**Resolved:** {ticket['resolved_at']}")
                    
                    # Internal notes section
                    st.markdown("---")
                    st.markdown("**📝 Internal Notes**")
                    
                    notes = get_ticket_notes(ticket['id'])
                    if notes:
                        for note in notes:
                            st.markdown(f"- *{note['created_at']}* by **{note['created_by']}**: {note['note']}")
                    else:
                        st.info("No internal notes yet")
                    
                    # Add note form
                    with st.form(f"add_note_{ticket['id']}"):
                        new_note = st.text_area("Add Internal Note", placeholder="Add a note for internal tracking...", key=f"note_text_{ticket['id']}")
                        note_author = st.text_input("Your Name", value="IT Support", key=f"note_author_{ticket['id']}")
                        
                        if st.form_submit_button("Add Note"):
                            if new_note:
                                add_ticket_note(ticket['id'], new_note, note_author)
                                st.success("Note added!")
                                st.rerun()
                            else:
                                st.error("Please enter a note")
                
                with col2:
                    st.markdown("**⚙️ Update Ticket**")
                    
                    # Status update with live dropdown
                    new_status = st.selectbox(
                        "Status",
                        ["Open", "In Progress", "Resolved", "Closed"],
                        index=["Open", "In Progress", "Resolved", "Closed"].index(ticket['status']),
                        key=f"status_{ticket['id']}"
                    )
                    
                    if new_status != ticket['status']:
                        if st.button("✅ Update Status", key=f"update_status_{ticket['id']}", type="primary"):
                            if update_ticket_status(ticket['id'], new_status):
                                st.success("Status updated!")
                                st.rerun()
                    
                    # Priority update
                    new_priority = st.selectbox(
                        "Priority",
                        ["Low", "Medium", "High", "Critical"],
                        index=["Low", "Medium", "High", "Critical"].index(ticket['priority']),
                        key=f"priority_{ticket['id']}"
                    )
                    
                    if new_priority != ticket['priority']:
                        if st.button("⚠️ Update Priority", key=f"update_priority_{ticket['id']}"):
                            if update_ticket_priority(ticket['id'], new_priority):
                                st.success("Priority updated!")
                                st.rerun()
                    
                    # Assignee update
                    new_assignee = st.text_input(
                        "Assign To",
                        value=ticket['assignee'],
                        key=f"assignee_{ticket['id']}"
                    )
                    
                    if new_assignee != ticket['assignee']:
                        if st.button("👤 Update Assignee", key=f"update_assignee_{ticket['id']}"):
                            if update_ticket_assignee(ticket['id'], new_assignee):
                                st.success("Assignee updated!")
                                st.rerun()
    else:
        st.info("No tickets found matching the filters.")

with tab2:
    st.markdown("### Create New Ticket")
    
    with st.form("create_ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            requester_name = st.text_input("Your Name *", value="Anonymous")
        with col2:
            department = st.text_input("Department", value="General")
        
        issue_summary = st.text_input("Issue Summary *", placeholder="Brief description of the issue", max_chars=200)
        description = st.text_area("Detailed Description *", placeholder="Detailed description of the issue", height=200)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category = st.selectbox("Category *", [
                "Network", "Authentication", "Email", "Hardware", 
                "Software", "Performance", "File Sharing", "Security", "Other"
            ])
        
        with col2:
            priority = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"], index=1)
        
        with col3:
            assignee = st.text_input("Assign To", value="Unassigned")
        
        tags = st.text_input("Tags (comma-separated)", placeholder="e.g., urgent, vpn, windows")
        
        submitted = st.form_submit_button("Create Ticket", use_container_width=True, type="primary")
        
        if submitted:
            if not issue_summary or not description:
                st.error("Please fill in all required fields (*)")
            else:
                ticket_id = create_ticket(
                    issue_summary=issue_summary,
                    description=description,
                    category=category,
                    priority=priority,
                    requester_name=requester_name,
                    department=department,
                    assignee=assignee,
                    tags=tags
                )
                st.success(f"✅ Ticket #{ticket_id} created successfully!")
                st.balloons()
                
                # Show ticket details
                st.markdown("### Ticket Created")
                st.markdown(f"**Ticket ID:** #{ticket_id}")
                st.markdown(f"**Issue Summary:** {issue_summary}")
                st.markdown(f"**Requester:** {requester_name} ({department})")
                st.markdown(f"**Category:** {category}")
                st.markdown(f"**Priority:** {priority}")
                st.markdown(f"**Assignee:** {assignee}")
                st.markdown(f"**Status:** Open")

with tab3:
    st.markdown("### Ticket Statistics")
    
    stats = get_ticket_stats()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Tickets", stats['total'])
    col2.metric("Open Tickets", stats['open'])
    col3.metric("Resolved Tickets", stats['resolved'])
    
    if stats['total'] > 0:
        resolution_rate = (stats['resolved'] / stats['total']) * 100
        col4.metric("Resolution Rate", f"{resolution_rate:.1f}%")
    else:
        col4.metric("Resolution Rate", "N/A")
    
    # Top categories
    if stats['top_categories']:
        st.markdown("### Top Issue Categories")
        
        df = pd.DataFrame(stats['top_categories'])
        
        # Bar chart
        st.bar_chart(df.set_index('category')['count'])
        
        # Table
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Recent tickets
    st.markdown("### Recent Tickets")
    recent_tickets = list_tickets()[:10]
    
    if recent_tickets:
        df_recent = pd.DataFrame(recent_tickets)
        df_recent = df_recent[['id', 'issue_summary', 'requester_name', 'category', 'status', 'priority', 'assignee', 'created_at']]
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
        st.info("No tickets yet")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>💡 Tip: Use descriptive summaries and detailed descriptions for faster resolution</small>
</div>
""", unsafe_allow_html=True)
