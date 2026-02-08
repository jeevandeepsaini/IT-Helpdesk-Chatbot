"""
Metrics Page - IT Helpdesk Chatbot
Analytics dashboard for compression and performance metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from src.metrics_store import get_aggregate_metrics, get_chat_history
from src.ticketing import get_ticket_stats

st.set_page_config(page_title="Metrics - IT Helpdesk", page_icon="📊", layout="wide")

st.title("📊 Analytics Dashboard")
st.markdown("Compression metrics, performance stats, and time savings")

# Get metrics
try:
    metrics = get_aggregate_metrics()
    ticket_stats = get_ticket_stats()
    
    # Key Metrics Row
    st.markdown("### 🎯 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "Total Chats",
        metrics['total_chats'],
        help="Total number of chat interactions"
    )
    
    col2.metric(
        "Auto-Resolution Rate",
        f"{metrics['auto_resolution_rate']:.1f}%",
        help="Percentage of queries resolved without ticket creation"
    )
    
    col3.metric(
        "Avg Compression Ratio",
        f"{metrics['avg_compression_ratio']:.2f}x",
        help="Average compression ratio for runtime context"
    )
    
    col4.metric(
        "Time Saved",
        f"{metrics['time_saved_hours']:.1f} hrs",
        help="Estimated time saved vs traditional support (4hr baseline)"
    )
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        "Tokens Saved",
        f"{metrics['total_tokens_saved']:,}",
        help="Total tokens saved through compression"
    )
    
    col2.metric(
        "Avg Latency",
        f"{metrics['avg_latency_ms']:.0f}ms",
        help="Average total response time"
    )
    
    col3.metric(
        "Resolved Queries",
        metrics['resolved_count'],
        help="Queries marked as resolved"
    )
    
    col4.metric(
        "Tickets Created",
        metrics['ticket_count'],
        help="Support tickets created from chat"
    )
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗜️ Compression Performance")
        
        # KB Compression
        if metrics['kb_total_chunks'] > 0:
            st.metric("KB Chunks", metrics['kb_total_chunks'])
            st.metric("KB Avg Compression", f"{metrics['kb_avg_compression_ratio']:.2f}x")
        
        # Compression ratio visualization
        if metrics['total_chats'] > 0:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['avg_compression_ratio'],
                title={'text': "Avg Runtime Compression Ratio"},
                gauge={
                    'axis': {'range': [None, 5]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 1.5], 'color': "lightgray"},
                        {'range': [1.5, 2.5], 'color': "lightblue"},
                        {'range': [2.5, 5], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 3
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Top Issue Categories")
        
        if metrics['top_categories']:
            df_categories = pd.DataFrame(metrics['top_categories'])
            
            fig = px.bar(
                df_categories,
                x='count',
                y='category',
                orientation='h',
                title='Chat Queries by Category',
                labels={'count': 'Number of Queries', 'category': 'Category'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available yet")
    
    # Charts Row 2
    st.markdown("---")
    st.markdown("### 🗜️ ScaleDown Compression Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Recent Compression Performance")
        
        # Get last 20 chat turns
        chat_history = get_chat_history()
        
        if chat_history:
            # Filter to last 20 with actual compression data
            recent_chats = [
                chat for chat in chat_history 
                if chat.get('runtime_original_tokens', 0) > 0
            ][:20]
            
            if recent_chats:
                # Create table
                table_data = []
                total_original = 0
                total_compressed = 0
                
                for chat in recent_chats:
                    original = chat.get('runtime_original_tokens', 0)
                    compressed = chat.get('runtime_compressed_tokens', 0)
                    saved = original - compressed
                    reduction_pct = (saved / original * 100) if original > 0 else 0
                    
                    total_original += original
                    total_compressed += compressed
                    
                    table_data.append({
                        'Query': chat.get('query', '')[:50] + '...' if len(chat.get('query', '')) > 50 else chat.get('query', ''),
                        'Category': chat.get('category', 'N/A'),
                        'Confidence': f"{chat.get('runtime_compression_ratio', 0):.2f}x",
                        'Tokens Saved': saved,
                        'Reduction %': f"{reduction_pct:.1f}%",
                        'Latency (ms)': f"{chat.get('scaledown_latency_ms', 0):.0f}"
                    })
                
                df_recent = pd.DataFrame(table_data)
                st.dataframe(df_recent, use_container_width=True, hide_index=True)
                
                # Summary metrics
                total_saved = total_original - total_compressed
                avg_reduction = (total_saved / total_original * 100) if total_original > 0 else 0
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Total Tokens Saved", f"{total_saved:,}")
                col_b.metric("Avg Token Reduction", f"{avg_reduction:.1f}%")
                col_c.metric("Total Original", f"{total_original:,}")
            else:
                st.info("No compression data available yet")
        else:
            st.info("No chat history available")
    
    with col2:
        st.markdown("#### Tokens: Before vs After Compression")
        
        if chat_history:
            recent_chats = [
                chat for chat in chat_history 
                if chat.get('runtime_original_tokens', 0) > 0
            ][:20]
            
            if recent_chats:
                import matplotlib.pyplot as plt
                
                # Prepare data
                indices = list(range(len(recent_chats)))
                original_tokens = [chat.get('runtime_original_tokens', 0) for chat in recent_chats]
                compressed_tokens = [chat.get('runtime_compressed_tokens', 0) for chat in recent_chats]
                
                # Create chart
                fig, ax = plt.subplots(figsize=(8, 5))
                
                bar_width = 0.35
                x = range(len(indices))
                
                ax.bar([i - bar_width/2 for i in x], original_tokens, bar_width, label='Before')
                ax.bar([i + bar_width/2 for i in x], compressed_tokens, bar_width, label='After')
                
                ax.set_xlabel('Chat Turn (most recent 20)')
                ax.set_ylabel('Tokens')
                ax.set_title('ScaleDown Compression: Before vs After')
                ax.legend()
                ax.grid(axis='y', alpha=0.3)
                
                st.pyplot(fig)
                plt.close()
            else:
                st.info("No compression data available yet")
        else:
            st.info("No chat history available")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏱️ Time Savings Breakdown")
        
        # Time savings calculation
        baseline_hours = metrics['resolved_count'] * 4  # 4 hours per traditional support
        chatbot_hours = metrics['resolved_count'] * 0.5  # 30 minutes per chatbot resolution
        time_saved = baseline_hours - chatbot_hours
        
        fig = go.Figure(data=[
            go.Bar(name='Traditional Support', x=['Time Required'], y=[baseline_hours]),
            go.Bar(name='Chatbot', x=['Time Required'], y=[chatbot_hours]),
            go.Bar(name='Time Saved', x=['Time Required'], y=[time_saved])
        ])
        fig.update_layout(
            title='Time Comparison (hours)',
            barmode='group',
            yaxis_title='Hours'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"""
        **Assumptions:**
        - Traditional support: 4 hours per issue (avg)
        - Chatbot resolution: 30 minutes per issue (avg)
        - **Total time saved: {time_saved:.1f} hours ({time_saved/8:.1f} work days)**
        """)
    
    with col2:
        st.markdown("### 🎫 Ticket Resolution")
        
        # Ticket stats pie chart
        if ticket_stats['total'] > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['Open', 'Resolved'],
                values=[ticket_stats['open'], ticket_stats['resolved']],
                hole=.3
            )])
            fig.update_layout(title='Ticket Status Distribution')
            st.plotly_chart(fig, use_container_width=True)
            
            resolution_rate = (ticket_stats['resolved'] / ticket_stats['total']) * 100
            st.metric("Ticket Resolution Rate", f"{resolution_rate:.1f}%")
        else:
            st.info("No ticket data available yet")
    
    # Chat History Table
    st.markdown("### 📜 Recent Chat History")
    
    chat_history = get_chat_history()
    
    if chat_history:
        df_history = pd.DataFrame(chat_history)
        
        # Select relevant columns
        display_cols = [
            'id', 'query', 'category', 'retrieved_chunks',
            'runtime_compression_ratio', 'total_latency_ms',
            'was_resolved', 'created_at'
        ]
        
        df_display = df_history[display_cols].copy()
        df_display['runtime_compression_ratio'] = df_display['runtime_compression_ratio'].round(2)
        df_display['total_latency_ms'] = df_display['total_latency_ms'].round(0)
        
        # Rename columns for display
        df_display.columns = [
            'ID', 'Query', 'Category', 'Chunks',
            'Compression', 'Latency (ms)',
            'Resolved', 'Timestamp'
        ]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Chat History CSV",
            data=csv,
            file_name="chat_history.csv",
            mime="text/csv"
        )
    else:
        st.info("No chat history available yet. Start chatting to see metrics!")
    
    # Cost Savings Estimate
    st.markdown("### 💰 Cost Savings Estimate")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Token Cost Savings**")
        # Assuming $0.002 per 1K tokens (example rate)
        token_cost_per_1k = 0.002
        cost_saved = (metrics['total_tokens_saved'] / 1000) * token_cost_per_1k
        st.metric("Estimated Savings", f"${cost_saved:.2f}")
        st.caption("Based on $0.002 per 1K tokens")
    
    with col2:
        st.markdown("**Labor Cost Savings**")
        # Assuming $50/hour for support staff
        hourly_rate = 50
        labor_saved = metrics['time_saved_hours'] * hourly_rate
        st.metric("Estimated Savings", f"${labor_saved:,.2f}")
        st.caption("Based on $50/hour support rate")
    
    with col3:
        st.markdown("**Total Estimated Savings**")
        total_saved = cost_saved + labor_saved
        st.metric("Total Savings", f"${total_saved:,.2f}")
        st.caption("Token + Labor savings")

except Exception as e:
    st.error(f"Error loading metrics: {e}")
    st.info("Start using the chatbot to generate metrics data")
    st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>📊 Metrics update in real-time as users interact with the chatbot</small>
</div>
""", unsafe_allow_html=True)
