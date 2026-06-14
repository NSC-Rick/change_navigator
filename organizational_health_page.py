import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import organizational_intelligence as org_intel

def organizational_health_page():
    """Organizational Health Dashboard - Intelligence for Change Leads"""
    st.markdown('<p class="main-header">🏥 Organizational Health</p>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Understand how the organization is experiencing change.</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Key Questions Section
    with st.expander("📌 Key Questions This Dashboard Answers", expanded=False):
        st.markdown("""
        1. **Which functional areas are struggling?**
        2. **Which locations are struggling?**
        3. **Where is change saturation occurring?**
        4. **Which projects are contributing to organizational pressure?**
        5. **Where should I spend my time this week?**
        """)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Functional Heat Map",
        "🌍 Geographic Heat Map", 
        "🗺️ Function × Location Matrix",
        "⚡ Change Saturation",
        "📈 Observation Coverage"
    ])
    
    # Tab 1: Functional Heat Map
    with tab1:
        st.subheader("Functional Heat Map")
        st.caption("Readiness scores aggregated by department with trend analysis")
        
        func_df = org_intel.get_functional_heat_map()
        
        if len(func_df) > 0:
            # Add color coding
            func_df['color'] = func_df['avg_readiness'].apply(org_intel.get_readiness_color_category)
            
            # Display table with formatting
            display_df = func_df[['department', 'avg_readiness', 'trend', 'observation_count', 'champion_count']].copy()
            display_df['avg_readiness'] = display_df['avg_readiness'].round(1)
            
            st.dataframe(
                display_df,
                column_config={
                    'department': 'Function',
                    'avg_readiness': st.column_config.NumberColumn('Readiness', format="%.1f"),
                    'trend': 'Trend',
                    'observation_count': 'Observations',
                    'champion_count': 'Champions'
                },
                hide_index=True,
                width="stretch"
            )
            
            # Visual chart
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    func_df.sort_values('avg_readiness'),
                    x='avg_readiness',
                    y='department',
                    orientation='h',
                    title='Readiness by Function',
                    labels={'avg_readiness': 'Average Readiness Score', 'department': 'Department'},
                    color='avg_readiness',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    range_color=[0, 10]
                )
                fig.add_vline(x=8.0, line_dash="dash", line_color="green", annotation_text="Target")
                fig.add_vline(x=6.0, line_dash="dash", line_color="orange", annotation_text="Caution")
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                # Trend summary
                st.markdown("### Trend Summary")
                trend_counts = func_df['trend'].value_counts()
                for trend, count in trend_counts.items():
                    emoji = "🔴" if trend == "Down" else "🟢" if trend == "Up" else "🟡"
                    st.metric(f"{emoji} {trend}", count)
                
                # At-risk departments
                st.markdown("### ⚠️ At-Risk Functions")
                at_risk = func_df[func_df['avg_readiness'] < 6.0]
                if len(at_risk) > 0:
                    for _, row in at_risk.iterrows():
                        st.warning(f"**{row['department']}**: {row['avg_readiness']:.1f} ({row['trend']})")
                else:
                    st.success("No functions below caution threshold")
        else:
            st.info("No functional data available yet. Submit observations to populate this view.")
    
    # Tab 2: Geographic Heat Map
    with tab2:
        st.subheader("Geographic Heat Map")
        st.caption("Readiness scores aggregated by location with trend analysis")
        
        geo_df = org_intel.get_geographic_heat_map()
        
        if len(geo_df) > 0:
            # Add color coding
            geo_df['color'] = geo_df['avg_readiness'].apply(org_intel.get_readiness_color_category)
            
            # Display table
            display_df = geo_df[['location', 'avg_readiness', 'trend', 'observation_count', 'champion_count']].copy()
            display_df['avg_readiness'] = display_df['avg_readiness'].round(1)
            
            st.dataframe(
                display_df,
                column_config={
                    'location': 'Location',
                    'avg_readiness': st.column_config.NumberColumn('Readiness', format="%.1f"),
                    'trend': 'Trend',
                    'observation_count': 'Observations',
                    'champion_count': 'Champions'
                },
                hide_index=True,
                width="stretch"
            )
            
            # Visual chart
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    geo_df.sort_values('avg_readiness'),
                    x='avg_readiness',
                    y='location',
                    orientation='h',
                    title='Readiness by Location',
                    labels={'avg_readiness': 'Average Readiness Score', 'location': 'Location'},
                    color='avg_readiness',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    range_color=[0, 10]
                )
                fig.add_vline(x=8.0, line_dash="dash", line_color="green", annotation_text="Target")
                fig.add_vline(x=6.0, line_dash="dash", line_color="orange", annotation_text="Caution")
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                # Trend summary
                st.markdown("### Trend Summary")
                trend_counts = geo_df['trend'].value_counts()
                for trend, count in trend_counts.items():
                    emoji = "🔴" if trend == "Down" else "🟢" if trend == "Up" else "🟡"
                    st.metric(f"{emoji} {trend}", count)
                
                # At-risk locations
                st.markdown("### ⚠️ At-Risk Locations")
                at_risk = geo_df[geo_df['avg_readiness'] < 6.0]
                if len(at_risk) > 0:
                    for _, row in at_risk.iterrows():
                        st.warning(f"**{row['location']}**: {row['avg_readiness']:.1f} ({row['trend']})")
                else:
                    st.success("No locations below caution threshold")
        else:
            st.info("No geographic data available yet. Ensure champions have location data.")
    
    # Tab 3: Function × Location Matrix
    with tab3:
        st.subheader("Function × Location Matrix")
        st.caption("Identify localized readiness issues across departments and locations")
        
        matrix_df = org_intel.get_function_location_matrix()
        
        if len(matrix_df) > 0 and not matrix_df.empty:
            # Create heatmap
            fig = px.imshow(
                matrix_df,
                labels=dict(x="Location", y="Department", color="Readiness"),
                x=matrix_df.columns,
                y=matrix_df.index,
                color_continuous_scale=['red', 'yellow', 'green'],
                aspect="auto",
                title="Readiness Heat Map: Department × Location"
            )
            fig.update_xaxes(side="bottom")
            st.plotly_chart(fig, width="stretch")
            
            # Show data table
            st.markdown("### Detailed Matrix")
            styled_df = matrix_df.round(1)
            st.dataframe(styled_df, width="stretch")
            
            # Insights
            st.markdown("### 🔍 Key Insights")
            
            # Find lowest scoring combinations
            matrix_flat = matrix_df.stack().reset_index()
            matrix_flat.columns = ['department', 'location', 'readiness']
            lowest = matrix_flat.nsmallest(3, 'readiness')
            
            st.markdown("**Lowest Readiness Combinations:**")
            for _, row in lowest.iterrows():
                color = org_intel.get_readiness_color_category(row['readiness'])
                emoji = "🔴" if color == "red" else "🟡" if color == "yellow" else "🟢"
                st.write(f"{emoji} **{row['department']}** in **{row['location']}**: {row['readiness']:.1f}")
        else:
            st.info("Insufficient data for matrix view. Need observations across multiple departments and locations.")
    
    # Tab 4: Change Saturation
    with tab4:
        st.subheader("Change Saturation View")
        st.caption("Active project impact by functional area")
        
        saturation_df = org_intel.get_change_saturation()
        
        if len(saturation_df) > 0:
            # Display table
            display_df = saturation_df.copy()
            display_df['avg_readiness'] = display_df['avg_readiness'].round(1)
            
            st.dataframe(
                display_df,
                column_config={
                    'department': 'Department',
                    'active_projects': 'Active Projects',
                    'champions_assigned': 'Champions',
                    'total_observations': 'Observations',
                    'avg_readiness': st.column_config.NumberColumn('Avg Readiness', format="%.1f")
                },
                hide_index=True,
                width="stretch"
            )
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    saturation_df.sort_values('active_projects', ascending=False),
                    x='department',
                    y='active_projects',
                    title='Active Projects by Department',
                    labels={'active_projects': 'Number of Active Projects', 'department': 'Department'},
                    color='active_projects',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                # Saturation + Readiness scatter
                fig = px.scatter(
                    saturation_df,
                    x='active_projects',
                    y='avg_readiness',
                    size='total_observations',
                    text='department',
                    title='Saturation vs Readiness',
                    labels={'active_projects': 'Active Projects', 'avg_readiness': 'Avg Readiness'},
                    color='avg_readiness',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    range_color=[0, 10]
                )
                fig.add_hline(y=6.0, line_dash="dash", line_color="orange")
                fig.update_traces(textposition='top center')
                st.plotly_chart(fig, width="stretch")
            
            # High saturation + low readiness alert
            st.markdown("### ⚠️ High Risk: Saturation + Low Readiness")
            high_risk = saturation_df[
                (saturation_df['active_projects'] >= 2) & 
                (saturation_df['avg_readiness'] < 6.0)
            ]
            
            if len(high_risk) > 0:
                for _, row in high_risk.iterrows():
                    st.error(
                        f"**{row['department']}**: {row['active_projects']} active projects, "
                        f"readiness {row['avg_readiness']:.1f}"
                    )
            else:
                st.success("No high-risk saturation situations detected")
        else:
            st.info("No saturation data available yet.")
    
    # Tab 5: Observation Coverage
    with tab5:
        st.subheader("Observation Coverage")
        st.caption("Participation metrics across projects, functions, and locations")
        
        # Time period selector
        days = st.selectbox("Time Period", [7, 14, 30], index=0, format_func=lambda x: f"Last {x} days")
        
        coverage_data = org_intel.get_observation_coverage(days=days)
        
        # Overall coverage
        st.markdown("### 📊 Overall Coverage")
        overall = coverage_data['overall']
        
        if len(overall) > 0:
            row = overall.iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Champions", int(row['total_champions']))
            
            with col2:
                st.metric("Active Champions", int(row['active_champions']))
            
            with col3:
                st.metric("Recent Observations", int(row['recent_observations']))
            
            with col4:
                coverage_pct = row['coverage_pct']
                st.metric("Coverage", f"{coverage_pct:.0f}%")
                if coverage_pct >= 80:
                    st.success("Excellent")
                elif coverage_pct >= 60:
                    st.warning("Good")
                else:
                    st.error("Needs Attention")
        
        # By Project
        st.markdown("### 📁 Coverage by Project")
        project_df = coverage_data['by_project']
        if len(project_df) > 0:
            st.dataframe(
                project_df,
                column_config={
                    'project_name': 'Project',
                    'total_champions': 'Total Champions',
                    'active_champions': 'Active Champions',
                    'recent_observations': 'Recent Observations',
                    'coverage_pct': st.column_config.NumberColumn('Coverage %', format="%.0f%%")
                },
                hide_index=True,
                width="stretch"
            )
        
        # By Department
        st.markdown("### 🏢 Coverage by Department")
        dept_df = coverage_data['by_department']
        if len(dept_df) > 0:
            st.dataframe(
                dept_df,
                column_config={
                    'department': 'Department',
                    'total_champions': 'Total Champions',
                    'active_champions': 'Active Champions',
                    'recent_observations': 'Recent Observations',
                    'coverage_pct': st.column_config.NumberColumn('Coverage %', format="%.0f%%")
                },
                hide_index=True,
                width="stretch"
            )
        
        # By Location
        st.markdown("### 🌍 Coverage by Location")
        location_df = coverage_data['by_location']
        if len(location_df) > 0:
            st.dataframe(
                location_df,
                column_config={
                    'location': 'Location',
                    'total_champions': 'Total Champions',
                    'active_champions': 'Active Champions',
                    'recent_observations': 'Recent Observations',
                    'coverage_pct': st.column_config.NumberColumn('Coverage %', format="%.0f%%")
                },
                hide_index=True,
                width="stretch"
            )
