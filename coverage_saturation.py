import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db
from datetime import datetime, timedelta

def render_coverage_saturation_tab(project_id, project):
    """Coverage & Saturation tab - Project-specific coverage and saturation metrics"""
    st.subheader("Coverage & Saturation Analysis")
    
    # Get project-specific data
    champions_df = db.get_champions_by_project(project_id)
    observations_df = db.get_observations_by_project(project_id)
    
    # Merge observations with champions to get department and location
    if len(observations_df) > 0 and len(champions_df) > 0:
        observations_df = observations_df.merge(
            champions_df[['id', 'champion_name', 'department', 'location']],
            left_on='champion_id',
            right_on='id',
            how='left',
            suffixes=('', '_champ')
        )
    
    # Defensive validation for required columns
    has_department = 'department' in champions_df.columns and champions_df['department'].notna().any()
    has_location = 'location' in champions_df.columns and champions_df['location'].notna().any()
    
    if len(champions_df) == 0:
        st.info("No champions assigned to this project yet. Add champions to see coverage metrics.")
        return
    
    # === OBSERVATION COVERAGE ===
    st.markdown("### 📊 Observation Coverage")
    st.markdown("*How well are we capturing field intelligence for this project?*")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_champions = len(champions_df)
        st.metric("Total Champions", total_champions)
    
    with col2:
        active_champions = len(champions_df[champions_df['observation_count'] > 0])
        st.metric("Active Champions", active_champions)
    
    with col3:
        participation_rate = (active_champions / total_champions * 100) if total_champions > 0 else 0
        st.metric("Participation Rate", f"{participation_rate:.0f}%")
    
    with col4:
        total_observations = len(observations_df)
        st.metric("Total Observations", total_observations)
    
    # Observation frequency analysis
    if len(observations_df) > 0:
        st.markdown("#### Observation Frequency")
        
        # Parse observation dates
        observations_df['observation_date'] = pd.to_datetime(observations_df['observation_date'])
        observations_df['week'] = observations_df['observation_date'].dt.to_period('W').astype(str)
        
        # Weekly observation counts
        weekly_obs = observations_df.groupby('week').size().reset_index(name='count')
        
        fig = px.line(
            weekly_obs,
            x='week',
            y='count',
            title='Observations per Week',
            labels={'week': 'Week', 'count': 'Observations'}
        )
        fig.update_traces(mode='lines+markers')
        st.plotly_chart(fig, use_container_width=True)
        
        # Average observations per champion
        avg_obs_per_champion = total_observations / total_champions if total_champions > 0 else 0
        st.metric("Average Observations per Champion", f"{avg_obs_per_champion:.1f}")
    
    st.markdown("---")
    
    # === CHAMPION COVERAGE ===
    st.markdown("### 👥 Champion Coverage")
    st.markdown("*Are we reaching all key functions and locations for this project?*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Department coverage
        st.markdown("#### Department Coverage")
        
        if has_department:
            dept_counts = champions_df['department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Champions']
            
            fig = px.bar(
                dept_counts,
                x='Department',
                y='Champions',
                title='Champions by Department',
                color='Champions',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            unique_departments = champions_df['department'].nunique()
            st.metric("Departments Covered", unique_departments)
        else:
            st.warning("⚠️ Department data unavailable. Please ensure champions have department information.")
    
    with col2:
        # Location coverage
        st.markdown("#### Location Coverage")
        
        if has_location:
            location_counts = champions_df['location'].value_counts().reset_index()
            location_counts.columns = ['Location', 'Champions']
            
            fig = px.bar(
                location_counts,
                x='Location',
                y='Champions',
                title='Champions by Location',
                color='Champions',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            unique_locations = champions_df['location'].nunique()
            st.metric("Locations Covered", unique_locations)
        else:
            st.warning("⚠️ Location data unavailable. Please ensure champions have location information.")
    
    st.markdown("---")
    
    # === CHANGE SATURATION ===
    st.markdown("### 🌡️ Change Saturation")
    st.markdown("*How is this project impacting the organization?*")
    
    if len(observations_df) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Readiness score trend
            st.markdown("#### Readiness Trend")
            
            observations_df_sorted = observations_df.sort_values('observation_date')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=observations_df_sorted['observation_date'],
                y=observations_df_sorted['readiness_score'],
                mode='lines+markers',
                name='Readiness Score',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            ))
            
            # Add average line
            avg_readiness = observations_df['readiness_score'].mean()
            fig.add_hline(
                y=avg_readiness,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Average: {avg_readiness:.1f}"
            )
            
            fig.update_layout(
                title='Readiness Score Over Time',
                xaxis_title='Date',
                yaxis_title='Readiness Score',
                yaxis_range=[0, 10],
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Overall status distribution
            st.markdown("#### Overall Status Distribution")
            
            status_counts = observations_df['overall_status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            # Define color mapping
            color_map = {
                'On Track': '#28a745',
                'At Risk': '#ffc107',
                'Off Track': '#dc3545'
            }
            
            fig = px.pie(
                status_counts,
                values='Count',
                names='Status',
                title='Project Status Distribution',
                color='Status',
                color_discrete_map=color_map
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Saturation indicators
        st.markdown("#### Saturation Indicators")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Recent observation rate
            recent_days = 30
            recent_date = datetime.now() - timedelta(days=recent_days)
            recent_obs = observations_df[observations_df['observation_date'] >= recent_date]
            recent_count = len(recent_obs)
            
            st.metric(
                f"Observations (Last {recent_days} Days)",
                recent_count,
                help=f"Number of observations in the last {recent_days} days"
            )
        
        with col2:
            # Average readiness
            avg_readiness = observations_df['readiness_score'].mean()
            readiness_trend = "↑" if avg_readiness >= 7 else "↓" if avg_readiness < 5 else "→"
            
            st.metric(
                "Average Readiness",
                f"{avg_readiness:.1f}/10",
                delta=readiness_trend,
                help="Average readiness score across all observations"
            )
        
        with col3:
            # At-risk percentage
            at_risk_count = len(observations_df[observations_df['overall_status'].isin(['At Risk', 'Off Track'])])
            at_risk_pct = (at_risk_count / len(observations_df) * 100) if len(observations_df) > 0 else 0
            
            st.metric(
                "At Risk / Off Track",
                f"{at_risk_pct:.0f}%",
                help="Percentage of observations indicating risk"
            )
    else:
        st.info("No observations yet. Champions can submit observations to see saturation metrics.")
    
    st.markdown("---")
    
    # === COVERAGE GAPS ===
    st.markdown("### 🔍 Coverage Gaps")
    st.markdown("*Where should we focus champion recruitment for this project?*")
    
    # Identify silent champions
    silent_champions = champions_df[champions_df['observation_count'] == 0]
    
    if len(silent_champions) > 0:
        st.warning(f"⚠️ **{len(silent_champions)} champion(s) have not submitted observations yet**")
        
        with st.expander("View Silent Champions"):
            for _, champion in silent_champions.iterrows():
                st.write(f"• **{champion['champion_name']}** - {champion['department']} ({champion['location']})")
    else:
        st.success("✅ All champions have submitted at least one observation!")
    
    # Department gaps
    if len(observations_df) > 0 and has_department and 'department' in observations_df.columns:
        dept_activity = observations_df.groupby('department').size().reset_index(name='observations')
        dept_champions = champions_df.groupby('department').size().reset_index(name='champions')
        
        dept_coverage = dept_champions.merge(dept_activity, on='department', how='left')
        dept_coverage['observations'] = dept_coverage['observations'].fillna(0)
        dept_coverage['obs_per_champion'] = dept_coverage['observations'] / dept_coverage['champions']
        
        low_coverage_depts = dept_coverage[dept_coverage['obs_per_champion'] < 1.0]
        
        if len(low_coverage_depts) > 0:
            st.warning(f"⚠️ **{len(low_coverage_depts)} department(s) with low observation coverage**")
            
            with st.expander("View Low Coverage Departments"):
                for _, dept in low_coverage_depts.iterrows():
                    st.write(
                        f"• **{dept['department']}**: {int(dept['observations'])} observations "
                        f"from {int(dept['champions'])} champion(s) "
                        f"({dept['obs_per_champion']:.1f} obs/champion)"
                    )
    elif len(observations_df) > 0 and not has_department:
        st.info("Department coverage analysis unavailable - department data missing.")
