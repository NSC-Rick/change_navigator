"""
Insights Tab - Simplified high-level insights for Initiative Workspace
"""
import streamlit as st
import pandas as pd
import database as db

def render_insights_tab(project_id, project):
    """Insights Tab - High-level insights summary"""
    
    st.markdown("### 📈 Initiative Insights")
    st.caption("Generated insights, sentiment summaries, and readiness trends")
    
    # Get observations data
    observations_df = db.get_observations_by_project(project_id)
    
    if len(observations_df) == 0:
        st.info("No observations yet. Insights will appear once champions submit field observations.")
        return
    
    # Readiness Overview
    st.markdown("#### 📊 Readiness Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Check if readiness_score column exists
    if 'readiness_score' in observations_df.columns:
        with col1:
            avg_readiness = observations_df['readiness_score'].mean()
            st.metric("Average Readiness", f"{avg_readiness:.1f}" if pd.notna(avg_readiness) else "N/A")
    else:
        with col1:
            st.metric("Average Readiness", "N/A")
    
    # Check if status column exists (could be 'status' or 'overall_status')
    status_col = None
    if 'status' in observations_df.columns:
        status_col = 'status'
    elif 'overall_status' in observations_df.columns:
        status_col = 'overall_status'
    
    if status_col:
        with col2:
            green_count = len(observations_df[observations_df[status_col] == 'Green'])
            green_pct = (green_count / len(observations_df) * 100) if len(observations_df) > 0 else 0
            st.metric("🟢 Green", f"{green_pct:.0f}%")
        
        with col3:
            yellow_count = len(observations_df[observations_df[status_col] == 'Yellow'])
            yellow_pct = (yellow_count / len(observations_df) * 100) if len(observations_df) > 0 else 0
            st.metric("🟡 Yellow", f"{yellow_pct:.0f}%")
        
        with col4:
            red_count = len(observations_df[observations_df[status_col] == 'Red'])
            red_pct = (red_count / len(observations_df) * 100) if len(observations_df) > 0 else 0
            st.metric("🔴 Red", f"{red_pct:.0f}%")
    else:
        with col2:
            st.metric("🟢 Green", "N/A")
        with col3:
            st.metric("🟡 Yellow", "N/A")
        with col4:
            st.metric("🔴 Red", "N/A")
        st.warning("⚠️ No status/readiness data available for current observations.")
        green_pct = 0
    
    st.markdown("---")
    
    # Sentiment Summary
    st.markdown("#### 💬 Sentiment Summary")
    
    if green_pct >= 60:
        sentiment = "Positive"
        sentiment_icon = "✅"
        sentiment_color = "green"
    elif green_pct >= 40:
        sentiment = "Mixed"
        sentiment_icon = "⚠️"
        sentiment_color = "orange"
    else:
        sentiment = "Concerned"
        sentiment_icon = "�"
        sentiment_color = "red"
    
    st.markdown(f"### {sentiment_icon} {sentiment}")
    st.caption(f"Based on {len(observations_df)} field observations")
    
    st.markdown("---")
    
    # Recent Observations
    st.markdown("#### 📝 Recent Observations")
    
    if 'observation_date' in observations_df.columns:
        recent_obs = observations_df.sort_values('observation_date', ascending=False).head(5)
        
        for idx, obs in recent_obs.iterrows():
            # Build title from available columns
            title_parts = []
            if 'champion_name' in obs:
                title_parts.append(obs['champion_name'])
            if 'department' in obs:
                title_parts.append(obs['department'])
            if 'observation_date' in obs:
                title_parts.append(f"({obs['observation_date']})")
            title = " - ".join(title_parts) if title_parts else "Observation"
            
            with st.expander(title):
                # Display available fields
                if status_col and status_col in obs:
                    st.write(f"**Status:** {obs[status_col]}")
                if 'readiness_score' in obs:
                    st.write(f"**Readiness Score:** {obs['readiness_score']}")
                if 'what_are_you_hearing' in obs:
                    st.write(f"**What's Happening:** {obs['what_are_you_hearing']}")
                if 'questions_emerging' in obs:
                    st.write(f"**Questions:** {obs['questions_emerging']}")
                if 'leadership_should_know' in obs:
                    st.write(f"**Leadership Should Know:** {obs['leadership_should_know']}")
    else:
        st.info("Observation details not available.")
    
    st.markdown("---")
    
    # Emerging Themes
    st.markdown("#### 🎯 Emerging Themes")
    st.info("Advanced theme analysis and trend detection will be available in future releases.")
    
    # Department Breakdown
    st.markdown("#### 🏢 Department Breakdown")
    
    if 'department' in observations_df.columns:
        # Build aggregation based on available columns
        agg_dict = {}
        if 'readiness_score' in observations_df.columns:
            agg_dict['readiness_score'] = 'mean'
        if 'id' in observations_df.columns:
            agg_dict['id'] = 'count'
        
        if agg_dict:
            dept_stats = observations_df.groupby('department').agg(agg_dict)
            if 'id' in dept_stats.columns:
                dept_stats = dept_stats.rename(columns={'id': 'observation_count'})
            dept_stats = dept_stats.reset_index()
            
            if 'readiness_score' in dept_stats.columns:
                dept_stats = dept_stats.sort_values('readiness_score', ascending=False)
            
            # Rename columns for display
            rename_map = {'department': 'Department'}
            if 'readiness_score' in dept_stats.columns:
                rename_map['readiness_score'] = 'Avg Readiness'
            if 'observation_count' in dept_stats.columns:
                rename_map['observation_count'] = 'Observations'
            
            st.dataframe(
                dept_stats.rename(columns=rename_map),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Department statistics not available.")
    else:
        st.info("Department data not available.")
