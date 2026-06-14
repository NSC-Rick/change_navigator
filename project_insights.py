import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db

def render_function_insights_tab(project_id, project):
    """Function Insights tab - Project-specific functional analysis"""
    st.subheader("Function Insights")
    st.caption(f"Functional analysis for {project['project_name']} only")
    
    # Get project-specific observations
    observations_df = db.get_observations_by_project(project_id)
    
    if len(observations_df) == 0:
        st.info("No observations available yet. Champions can submit observations to populate this view.")
        return
    
    # Aggregate by department for THIS PROJECT ONLY
    dept_stats = observations_df.groupby('department').agg({
        'readiness_score': ['mean', 'count'],
        'overall_status': lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    dept_stats.columns = ['department', 'avg_readiness', 'observation_count', 'status_dist']
    dept_stats = dept_stats.sort_values('avg_readiness')
    
    # Calculate trend (last 30 days vs previous 30 days)
    from datetime import datetime, timedelta
    now = datetime.now()
    thirty_days_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    sixty_days_ago = (now - timedelta(days=60)).strftime("%Y-%m-%d")
    
    recent_obs = observations_df[observations_df['observation_date'] >= thirty_days_ago]
    previous_obs = observations_df[
        (observations_df['observation_date'] >= sixty_days_ago) & 
        (observations_df['observation_date'] < thirty_days_ago)
    ]
    
    if len(recent_obs) > 0 and len(previous_obs) > 0:
        recent_avg = recent_obs.groupby('department')['readiness_score'].mean()
        previous_avg = previous_obs.groupby('department')['readiness_score'].mean()
        
        dept_stats['trend'] = dept_stats['department'].apply(
            lambda d: 'Up' if d in recent_avg and d in previous_avg and recent_avg[d] > previous_avg[d] 
            else 'Down' if d in recent_avg and d in previous_avg and recent_avg[d] < previous_avg[d]
            else 'Stable'
        )
    else:
        dept_stats['trend'] = 'Stable'
    
    # Display summary table
    st.markdown("### Functional Readiness Summary")
    
    display_df = dept_stats[['department', 'avg_readiness', 'observation_count', 'trend']].copy()
    display_df['avg_readiness'] = display_df['avg_readiness'].round(1)
    
    st.dataframe(
        display_df,
        column_config={
            'department': 'Function',
            'avg_readiness': st.column_config.NumberColumn('Readiness', format="%.1f"),
            'observation_count': 'Observations',
            'trend': 'Trend (30d)'
        },
        hide_index=True,
        width="stretch"
    )
    
    # Visual charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Readiness by Function")
        fig = px.bar(
            dept_stats,
            x='avg_readiness',
            y='department',
            orientation='h',
            labels={'avg_readiness': 'Average Readiness Score', 'department': 'Function'},
            color='avg_readiness',
            color_continuous_scale=['red', 'yellow', 'green'],
            range_color=[0, 10]
        )
        fig.add_vline(x=8.0, line_dash="dash", line_color="green", annotation_text="Target")
        fig.add_vline(x=6.0, line_dash="dash", line_color="orange", annotation_text="Caution")
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.markdown("### Observation Volume")
        fig = px.bar(
            dept_stats.sort_values('observation_count', ascending=False),
            x='department',
            y='observation_count',
            labels={'observation_count': 'Number of Observations', 'department': 'Function'},
            color='avg_readiness',
            color_continuous_scale=['red', 'yellow', 'green']
        )
        st.plotly_chart(fig, width="stretch")
    
    # At-risk functions
    st.markdown("---")
    st.markdown("### ⚠️ Functions Requiring Attention")
    
    at_risk = dept_stats[dept_stats['avg_readiness'] < 6.0]
    
    if len(at_risk) > 0:
        for _, row in at_risk.iterrows():
            st.warning(
                f"**{row['department']}**: Readiness {row['avg_readiness']:.1f} "
                f"({row['observation_count']} observations, trend: {row['trend']})"
            )
    else:
        st.success("✅ All functions are above the caution threshold (6.0)")
    
    # Recent observations by function
    st.markdown("---")
    st.markdown("### Recent Observations by Function")
    
    selected_dept = st.selectbox(
        "Select Function",
        options=['All'] + sorted(dept_stats['department'].tolist()),
        key=f"func_insights_dept_{project_id}"
    )
    
    if selected_dept != 'All':
        filtered_obs = observations_df[observations_df['department'] == selected_dept]
    else:
        filtered_obs = observations_df
    
    for _, obs in filtered_obs.head(5).iterrows():
        status_emoji = "🟢" if obs['overall_status'] == 'Green' else "🟡" if obs['overall_status'] == 'Yellow' else "🔴"
        with st.expander(
            f"{status_emoji} {obs['champion_name']} - {obs['department']} "
            f"({obs['observation_date'][:10]}) - Score: {obs['readiness_score']}/10"
        ):
            st.markdown(f"**What are you hearing?**\n{obs['what_are_you_hearing']}")
            st.markdown(f"**Questions emerging?**\n{obs['questions_emerging']}")
            st.markdown(f"**Leadership should know:**\n{obs['leadership_should_know']}")

def render_location_insights_tab(project_id, project):
    """Location Insights tab - Project-specific geographic analysis"""
    st.subheader("Location Insights")
    st.caption(f"Geographic analysis for {project['project_name']} only")
    
    # Get project-specific champions and observations
    champions_df = db.get_champions_by_project(project_id)
    observations_df = db.get_observations_by_project(project_id)
    
    if 'location' not in champions_df.columns or champions_df['location'].isna().all():
        st.warning("Location data not available. Please ensure champions have location information.")
        return
    
    if len(observations_df) == 0:
        st.info("No observations available yet. Champions can submit observations to populate this view.")
        return
    
    # Merge observations with champion location data
    obs_with_location = observations_df.merge(
        champions_df[['id', 'location']], 
        left_on='champion_id', 
        right_on='id', 
        how='left',
        suffixes=('', '_champ')
    )
    
    # Aggregate by location for THIS PROJECT ONLY
    location_stats = obs_with_location.groupby('location').agg({
        'readiness_score': ['mean', 'count'],
        'overall_status': lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    location_stats.columns = ['location', 'avg_readiness', 'observation_count', 'status_dist']
    location_stats = location_stats.sort_values('avg_readiness')
    
    # Calculate trend
    from datetime import datetime, timedelta
    now = datetime.now()
    thirty_days_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    sixty_days_ago = (now - timedelta(days=60)).strftime("%Y-%m-%d")
    
    recent_obs = obs_with_location[obs_with_location['observation_date'] >= thirty_days_ago]
    previous_obs = obs_with_location[
        (obs_with_location['observation_date'] >= sixty_days_ago) & 
        (obs_with_location['observation_date'] < thirty_days_ago)
    ]
    
    if len(recent_obs) > 0 and len(previous_obs) > 0:
        recent_avg = recent_obs.groupby('location')['readiness_score'].mean()
        previous_avg = previous_obs.groupby('location')['readiness_score'].mean()
        
        location_stats['trend'] = location_stats['location'].apply(
            lambda loc: 'Up' if loc in recent_avg and loc in previous_avg and recent_avg[loc] > previous_avg[loc] 
            else 'Down' if loc in recent_avg and loc in previous_avg and recent_avg[loc] < previous_avg[loc]
            else 'Stable'
        )
    else:
        location_stats['trend'] = 'Stable'
    
    # Display summary table
    st.markdown("### Location Readiness Summary")
    
    display_df = location_stats[['location', 'avg_readiness', 'observation_count', 'trend']].copy()
    display_df['avg_readiness'] = display_df['avg_readiness'].round(1)
    
    st.dataframe(
        display_df,
        column_config={
            'location': 'Location',
            'avg_readiness': st.column_config.NumberColumn('Readiness', format="%.1f"),
            'observation_count': 'Observations',
            'trend': 'Trend (30d)'
        },
        hide_index=True,
        width="stretch"
    )
    
    # Visual charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Readiness by Location")
        fig = px.bar(
            location_stats,
            x='avg_readiness',
            y='location',
            orientation='h',
            labels={'avg_readiness': 'Average Readiness Score', 'location': 'Location'},
            color='avg_readiness',
            color_continuous_scale=['red', 'yellow', 'green'],
            range_color=[0, 10]
        )
        fig.add_vline(x=8.0, line_dash="dash", line_color="green", annotation_text="Target")
        fig.add_vline(x=6.0, line_dash="dash", line_color="orange", annotation_text="Caution")
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.markdown("### Champion Distribution")
        champion_counts = champions_df['location'].value_counts().reset_index()
        champion_counts.columns = ['location', 'count']
        
        fig = px.pie(
            champion_counts,
            values='count',
            names='location',
            title='Champions by Location'
        )
        st.plotly_chart(fig, width="stretch")
    
    # At-risk locations
    st.markdown("---")
    st.markdown("### ⚠️ Locations Requiring Attention")
    
    at_risk = location_stats[location_stats['avg_readiness'] < 6.0]
    
    if len(at_risk) > 0:
        for _, row in at_risk.iterrows():
            st.warning(
                f"**{row['location']}**: Readiness {row['avg_readiness']:.1f} "
                f"({row['observation_count']} observations, trend: {row['trend']})"
            )
    else:
        st.success("✅ All locations are above the caution threshold (6.0)")
    
    # Function × Location Matrix
    st.markdown("---")
    st.markdown("### Function × Location Matrix")
    st.caption("Identify localized readiness patterns")
    
    if len(obs_with_location) > 0:
        matrix_data = obs_with_location.pivot_table(
            values='readiness_score',
            index='department',
            columns='location',
            aggfunc='mean'
        )
        
        if not matrix_data.empty:
            fig = px.imshow(
                matrix_data,
                labels=dict(x="Location", y="Function", color="Readiness"),
                x=matrix_data.columns,
                y=matrix_data.index,
                color_continuous_scale=['red', 'yellow', 'green'],
                aspect="auto",
                zmin=0,
                zmax=10
            )
            fig.update_xaxes(side="bottom")
            st.plotly_chart(fig, width="stretch")
            
            # Show data table
            st.markdown("**Detailed Matrix Values:**")
            styled_df = matrix_data.round(1)
            st.dataframe(styled_df, width="stretch")
        else:
            st.info("Insufficient data for matrix view. Need observations across multiple functions and locations.")
    
    # Recent observations by location
    st.markdown("---")
    st.markdown("### Recent Observations by Location")
    
    selected_location = st.selectbox(
        "Select Location",
        options=['All'] + sorted(location_stats['location'].tolist()),
        key=f"loc_insights_loc_{project_id}"
    )
    
    if selected_location != 'All':
        filtered_obs = obs_with_location[obs_with_location['location'] == selected_location]
    else:
        filtered_obs = obs_with_location
    
    for _, obs in filtered_obs.head(5).iterrows():
        status_emoji = "🟢" if obs['overall_status'] == 'Green' else "🟡" if obs['overall_status'] == 'Yellow' else "🔴"
        location_display = obs.get('location', 'Unknown')
        with st.expander(
            f"{status_emoji} {obs['champion_name']} - {obs['department']} ({location_display}) "
            f"({obs['observation_date'][:10]}) - Score: {obs['readiness_score']}/10"
        ):
            st.markdown(f"**What are you hearing?**\n{obs['what_are_you_hearing']}")
            st.markdown(f"**Questions emerging?**\n{obs['questions_emerging']}")
            st.markdown(f"**Leadership should know:**\n{obs['leadership_should_know']}")
