"""
Executive Dashboard Tab - Sponsor-facing view for Initiative Workspace
"""
import streamlit as st
import pandas as pd
import database as db
from datetime import datetime
from summary_utils import generate_placeholder_summary

def render_executive_dashboard_tab(project_id, project):
    """Executive Dashboard - Sponsor-facing view with high-level insights"""
    
    st.markdown("### 🎯 Executive Dashboard")
    st.caption("Leadership-focused view of initiative health and readiness")
    
    # Get data
    stats = db.get_project_stats(project_id)
    observations_df = db.get_observations_by_project(project_id)
    
    # Top-level metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        readiness = stats.get('avg_readiness_score', 0)
        if pd.notna(readiness) and readiness > 0:
            readiness_display = f"{readiness:.1f}/10"
            if readiness >= 8:
                st.metric("🎯 Readiness", readiness_display, delta="Strong", delta_color="normal")
            elif readiness >= 6:
                st.metric("🎯 Readiness", readiness_display, delta="Moderate", delta_color="normal")
            else:
                st.metric("🎯 Readiness", readiness_display, delta="Developing", delta_color="inverse")
        else:
            st.metric("🎯 Readiness", "N/A")
    
    with col2:
        obs_count = stats.get('observation_count', 0)
        st.metric("📝 Field Reports", int(obs_count))
    
    with col3:
        if len(observations_df) > 0:
            recent_obs = observations_df.tail(10)
            green_pct = (recent_obs['overall_status'] == 'Green').sum() / len(recent_obs) * 100
            if green_pct >= 70:
                sentiment = "Positive"
                st.metric("📊 Sentiment", sentiment, delta="✅", delta_color="normal")
            elif green_pct >= 40:
                sentiment = "Mixed"
                st.metric("📊 Sentiment", sentiment, delta="⚠️", delta_color="off")
            else:
                sentiment = "Concerned"
                st.metric("📊 Sentiment", sentiment, delta="🚨", delta_color="inverse")
        else:
            st.metric("📊 Sentiment", "No Data")
    
    st.markdown("---")
    
    # Executive Summary Section
    st.markdown("### 📋 Executive Summary")
    
    latest_summary = db.get_latest_summary(project_id)
    
    if latest_summary:
        # Display summary in styled card
        st.markdown('<div class="executive-summary">', unsafe_allow_html=True)
        
        # Header with date
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("#### Key Insights")
        with col2:
            st.caption(f"Generated: {latest_summary['summary_date']}")
        
        # Summary content
        st.markdown(latest_summary['summary_text'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("📊 No executive summary generated yet.")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🤖 Generate Executive Summary", type="primary", use_container_width=True):
            if len(observations_df) == 0:
                st.warning("No observations available to generate summary.")
            else:
                with st.spinner("Analyzing field observations..."):
                    summary_text = generate_placeholder_summary(observations_df, project['project_name'])
                    
                    db.add_ai_summary(
                        project_id=project_id,
                        summary_text=summary_text
                    )
                
                st.success("✅ Executive summary generated!")
                st.rerun()
    
    st.markdown("---")
    
    # Risk Indicators
    if len(observations_df) > 0:
        st.markdown("### ⚠️ Risk Indicators")
        
        # Calculate risk metrics
        red_count = (observations_df['overall_status'] == 'Red').sum()
        yellow_count = (observations_df['overall_status'] == 'Yellow').sum()
        low_readiness = (observations_df['readiness_score'] < 5).sum()
        
        risk_col1, risk_col2, risk_col3 = st.columns(3)
        
        with risk_col1:
            if red_count > 0:
                st.error(f"🚨 {red_count} Concerned Reports")
            else:
                st.success("✅ No Concerned Reports")
        
        with risk_col2:
            if yellow_count > 0:
                st.warning(f"⚠️ {yellow_count} Mixed Reports")
            else:
                st.success("✅ No Mixed Reports")
        
        with risk_col3:
            if low_readiness > 0:
                st.error(f"📉 {low_readiness} Low Readiness Scores")
            else:
                st.success("✅ No Low Readiness Scores")
    
    st.markdown("---")
    
    # Recommended Actions
    st.markdown("### 🎯 Recommended Actions")
    
    if len(observations_df) > 0:
        avg_readiness = observations_df['readiness_score'].mean()
        
        if avg_readiness < 6:
            st.markdown("""
            **Immediate Actions Required:**
            1. 🔴 Conduct stakeholder listening sessions to address concerns
            2. 📋 Publish FAQ addressing recurring questions
            3. 👥 Increase champion touchpoints and support
            """)
        elif avg_readiness < 8:
            st.markdown("""
            **Focus Areas:**
            1. 🟡 Address specific concerns raised in field observations
            2. 📢 Reinforce key messages through leadership
            3. 🔄 Continue champion engagement and feedback loops
            """)
        else:
            st.markdown("""
            **Sustain Momentum:**
            1. 🟢 Identify and amplify success stories
            2. 💪 Maintain regular champion touchpoints
            3. 🚀 Prepare for launch - ensure support resources are ready
            """)
    else:
        st.info("No observations yet. Recommended actions will appear once field reports are submitted.")
