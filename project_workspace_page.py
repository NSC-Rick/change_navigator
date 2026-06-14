import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db
from datetime import datetime
from executive_dashboard import render_executive_dashboard_tab
from insights_tab import render_insights_tab
from summary_utils import generate_placeholder_summary
from geocoding import geocode_location
from map_tab import render_map_tab

def initiative_workspace_page():
    """Initiative Workspace - Central hub for all initiative activities"""
    
    # Check if initiative is selected
    if 'active_project_id' not in st.session_state:
        st.warning("⚠️ No initiative configured.")
        st.info("Please create or configure an initiative to use the Initiative Workspace.")
        
        # Check if any projects exist
        try:
            projects_df = db.get_all_projects()
            if len(projects_df) == 0:
                st.markdown("### Get Started")
                st.markdown("1. Go to **Administration** page")
                st.markdown("2. Click **Load Sample Data** to create a demo initiative")
                st.markdown("3. Or create a new initiative from the **Change Manager Dashboard**")
            elif len(projects_df) == 1:
                # Auto-select the single project
                project = projects_df.iloc[0]
                st.session_state.active_project_id = project['id']
                st.session_state.active_project_name = project['project_name']
                st.rerun()
            else:
                st.markdown("### Multiple Initiatives Found")
                st.markdown("Please select an initiative from the **Change Manager Dashboard**.")
                if st.button("Go to Dashboard"):
                    st.session_state.current_page = "Change Manager Dashboard"
                    st.rerun()
        except Exception:
            st.error("Database not initialized. Please go to Administration page and initialize the database.")
        return
    
    project_id = st.session_state.active_project_id
    project = db.get_project_by_id(project_id)
    
    if not project:
        st.error("Project not found.")
        if 'active_project_id' in st.session_state:
            del st.session_state.active_project_id
        return
    
    # Archived initiative banner
    if project.get('status') == 'Archived':
        st.warning("⚠️ **This initiative is archived.** No new data can be added to archived initiatives.")
        st.markdown("---")
    
    # Initiative Header with Back button
    col_header, col_back = st.columns([4, 1])
    
    with col_header:
        st.markdown(f'<p class="main-header">{project["project_name"]}</p>', unsafe_allow_html=True)
        st.caption(f"Sponsor: {project['sponsor_name']} | Status: {project['status']}")
    
    with col_back:
        if st.button("← Back to Dashboard", use_container_width=True):
            if 'active_project_id' in st.session_state:
                del st.session_state.active_project_id
            st.session_state.current_page = "Change Manager Dashboard"
            st.rerun()
    
    st.markdown("---")
    
    # Summary Cards
    stats = db.get_project_stats(project_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        readiness = stats.get('avg_readiness_score', 0)
        if pd.notna(readiness) and readiness > 0:
            readiness_display = f"{readiness:.1f}/10"
            delta_color = "normal" if readiness >= 7 else "inverse"
        else:
            readiness_display = "N/A"
            delta_color = "off"
        st.metric("🎯 Overall Readiness", readiness_display)
    
    with col2:
        obs_count = stats.get('observation_count', 0)
        st.metric("📝 Field Reports", int(obs_count))
    
    with col3:
        champion_count = stats.get('champion_count', 0)
        active_champions = len(db.get_champions_by_project(project_id)[db.get_champions_by_project(project_id)['observation_count'] > 0]) if champion_count > 0 else 0
        participation = f"{int(active_champions)}/{int(champion_count)}"
        st.metric("👥 Champion Participation", participation)
    
    with col4:
        # Get latest observations to determine sentiment
        observations_df = db.get_observations_by_project(project_id)
        if len(observations_df) > 0:
            recent_obs = observations_df.tail(10)
            green_pct = (recent_obs['overall_status'] == 'Green').sum() / len(recent_obs) * 100
            if green_pct >= 70:
                sentiment = "Positive"
                sentiment_icon = "✅"
            elif green_pct >= 40:
                sentiment = "Mixed"
                sentiment_icon = "⚠️"
            else:
                sentiment = "Concerned"
                sentiment_icon = "🚨"
        else:
            sentiment = "No Data"
            sentiment_icon = "⚪"
        st.metric("📊 Sentiment", f"{sentiment_icon} {sentiment}")
    
    st.markdown("---")
    
    # Initialize workspace section in session state
    if 'workspace_section' not in st.session_state:
        st.session_state.workspace_section = "Overview"
    
    # Session-state-backed navigation for Initiative Workspace (simplified structure)
    workspace_section = st.radio(
        "Workspace Section",
        options=[
            "📊 Overview",
            "📝 Observations",
            "� Insights",
            "�️ Map",
            "⚙️ Settings"
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="workspace_section"
    )
    
    st.markdown("---")
    
    # Render selected section
    if workspace_section == "📊 Overview":
        render_overview_tab(project_id, project)
    elif workspace_section == "📝 Observations":
        render_observations_tab(project_id, project)
    elif workspace_section == "� Insights":
        render_insights_tab(project_id, project)
    elif workspace_section == "�️ Map":
        render_map_tab(project_id, project)
    elif workspace_section == "⚙️ Settings":
        render_initiative_settings_tab(project_id, project)

def render_overview_tab(project_id, project):
    """Overview tab - Key metrics and trends"""
    st.subheader("Initiative Overview")
    
    stats = db.get_project_stats(project_id)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Champions", int(stats.get('champion_count', 0)))
    
    with col2:
        st.metric("Observations", int(stats.get('observation_count', 0)))
    
    with col3:
        avg_readiness = stats.get('avg_readiness_score')
        if pd.notna(avg_readiness):
            st.metric("Avg Readiness", f"{avg_readiness:.1f}")
        else:
            st.metric("Avg Readiness", "N/A")
    
    with col4:
        if stats.get('champion_count', 0) > 0:
            active_champions = stats.get('observation_count', 0) / stats.get('champion_count', 1)
            participation = min(100, (active_champions / 1) * 100)
            st.metric("Participation", f"{participation:.0f}%")
        else:
            st.metric("Participation", "N/A")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Readiness Trend")
        trend_df = db.get_readiness_trend(project_id)
        
        if len(trend_df) > 0:
            fig = px.line(trend_df, x='date', y='avg_readiness', 
                         title='Average Readiness Over Time',
                         labels={'date': 'Date', 'avg_readiness': 'Readiness Score'})
            fig.update_layout(yaxis_range=[0, 10])
            fig.add_hline(y=8, line_dash="dash", line_color="green", annotation_text="Target")
            fig.add_hline(y=6, line_dash="dash", line_color="orange", annotation_text="Caution")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No trend data available yet.")
    
    with col2:
        st.subheader("Observations by Department")
        dept_df = db.get_observations_by_department(project_id)
        
        if len(dept_df) > 0:
            fig = px.bar(dept_df, x='department', y='observation_count',
                        title='Observation Count by Department',
                        labels={'department': 'Department', 'observation_count': 'Observations'},
                        color='avg_readiness',
                        color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No department data available yet.")
    
    # Recent Observations
    st.markdown("---")
    st.subheader("Recent Observations")
    
    observations_df = db.get_observations_by_project(project_id)
    
    if len(observations_df) > 0:
        for _, obs in observations_df.head(5).iterrows():
            with st.expander(f"{get_status_color(obs['overall_status'])} {obs['champion_name']} - {obs['department']} ({obs['observation_date'][:10]})"):
                st.markdown(f"**Readiness Score:** {obs['readiness_score']}/10")
                st.markdown(f"**What are you hearing?**\n{obs['what_are_you_hearing']}")
                st.markdown(f"**Questions emerging?**\n{obs['questions_emerging']}")
                st.markdown(f"**Leadership should know:**\n{obs['leadership_should_know']}")
    else:
        st.info("No observations yet. Champions can submit observations from the Submit Field Observation page.")

def render_champions_tab(project_id, project):
    """Champions tab - Champion management"""
    st.subheader("Champions")
    
    champions_df = db.get_champions_by_project(project_id)
    
    # Handle edit champion modal
    if 'editing_champion_id' in st.session_state:
        champion_to_edit = champions_df[champions_df['id'] == st.session_state.editing_champion_id].iloc[0]
        
        st.markdown("### Edit Champion")
        
        with st.form(f"edit_champion_form_{st.session_state.editing_champion_id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_name = st.text_input("Champion Name *", value=champion_to_edit['champion_name'])
                edit_department = st.text_input("Department *", value=champion_to_edit['department'])
                edit_location = st.text_input("Location *", value=champion_to_edit['location'] if champion_to_edit['location'] else "", help="e.g., Boston, MA or Toronto, ON or London, UK")
                edit_email = st.text_input("Email *", value=champion_to_edit['email'])
            
            with col2:
                edit_role = st.text_input("Role *", value=champion_to_edit['role'])
                edit_business_unit = st.text_input("Business Unit", value=champion_to_edit.get('business_unit', '') if champion_to_edit.get('business_unit') else "")
                edit_manager = st.text_input("Manager", value=champion_to_edit.get('manager', '') if champion_to_edit.get('manager') else "")
                edit_region = st.text_input("Region", value=champion_to_edit.get('region', '') if champion_to_edit.get('region') else "")
            
            col_save, col_cancel = st.columns([1, 1])
            
            with col_save:
                save_button = st.form_submit_button("💾 Save Changes", type="primary")
            
            with col_cancel:
                cancel_button = st.form_submit_button("❌ Cancel")
            
            if save_button:
                if not edit_name or not edit_department or not edit_location or not edit_email or not edit_role:
                    st.error("Please fill in all required fields (marked with *).")
                else:
                    # Check if location can be geocoded
                    coords = geocode_location(edit_location)
                    
                    success = db.update_champion(
                        champion_id=st.session_state.editing_champion_id,
                        champion_name=edit_name,
                        department=edit_department,
                        location=edit_location,
                        email=edit_email,
                        role=edit_role,
                        business_unit=edit_business_unit if edit_business_unit else None,
                        manager=edit_manager if edit_manager else None,
                        region=edit_region if edit_region else None
                    )
                    
                    if success:
                        if coords["resolved"]:
                            st.success(f"✅ Champion '{edit_name}' updated successfully! Location mapped to coordinates.")
                        else:
                            st.success(f"✅ Champion '{edit_name}' updated successfully!")
                            st.warning(f"⚠️ Location '{edit_location}' could not be automatically mapped. The champion will not appear on the Location Insights map until coordinates are available.")
                        del st.session_state.editing_champion_id
                        st.rerun()
                    else:
                        st.error("Failed to update champion. Please try again.")
            
            if cancel_button:
                del st.session_state.editing_champion_id
                st.rerun()
        
        st.markdown("---")
    
    # Handle delete champion confirmation
    if 'deleting_champion_id' in st.session_state:
        champion_to_delete = champions_df[champions_df['id'] == st.session_state.deleting_champion_id].iloc[0]
        
        st.warning(f"⚠️ **Confirm Deletion**")
        st.write(f"Are you sure you want to delete champion **{champion_to_delete['champion_name']}**?")
        
        if int(champion_to_delete['observation_count']) > 0:
            st.error(
                f"⚠️ This champion has {int(champion_to_delete['observation_count'])} observation(s). "
                "Deleting this champion will remove their record but preserve observation history."
            )
        
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("🗑️ Confirm Delete", type="primary"):
                success = db.delete_champion(st.session_state.deleting_champion_id)
                if success:
                    st.success(f"✅ Champion '{champion_to_delete['champion_name']}' deleted successfully!")
                    del st.session_state.deleting_champion_id
                    st.rerun()
                else:
                    st.error(
                        f"⚠️ Cannot delete champion '{champion_to_delete['champion_name']}' "
                        f"because they have {int(champion_to_delete['observation_count'])} observation(s). "
                        "Please delete or reassign their observations first."
                    )
        
        with col2:
            if st.button("❌ Cancel"):
                del st.session_state.deleting_champion_id
                st.rerun()
        
        st.markdown("---")
    
    if len(champions_df) > 0:
        # Display champions with action buttons
        for idx, champion in champions_df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1.5, 2, 1, 1])
                
                with col1:
                    st.write(f"**{champion['champion_name']}**")
                    st.caption(f"📧 {champion['email']}")
                
                with col2:
                    st.write(champion['department'])
                    st.caption("Department")
                
                with col3:
                    location_display = champion['location'] if champion['location'] else 'Unknown'
                    st.write(location_display)
                    st.caption("Location")
                
                with col4:
                    st.write(champion['role'])
                    st.caption("Role")
                
                with col5:
                    st.metric("Obs", int(champion['observation_count']))
                
                with col6:
                    # Edit button
                    if st.button("✏️ Edit", key=f"edit_{champion['id']}", help="Edit champion"):
                        st.session_state.editing_champion_id = champion['id']
                        st.rerun()
                    
                    # Delete button
                    if st.button("🗑️", key=f"delete_{champion['id']}", help="Delete champion"):
                        st.session_state.deleting_champion_id = champion['id']
                        st.rerun()
                
                st.markdown("---")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Champions", len(champions_df))
        
        with col2:
            active_champions = len(champions_df[champions_df['observation_count'] > 0])
            participation_rate = (active_champions / len(champions_df) * 100) if len(champions_df) > 0 else 0
            st.metric("Participation Rate", f"{participation_rate:.0f}%")
        
        with col3:
            if 'location' in champions_df.columns:
                unique_locations = champions_df['location'].nunique()
                st.metric("Locations", unique_locations)
    else:
        st.info("No champions assigned to this project yet.")
    
    st.markdown("---")
    st.subheader("Add New Champion")
    
    with st.form("add_champion_workspace"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Champion Name *")
            new_department = st.text_input("Department *")
            new_location = st.text_input("Location *", help="e.g., Boston, MA or Toronto, ON or London, UK")
            new_email = st.text_input("Email *")
        
        with col2:
            new_role = st.text_input("Role *")
            new_business_unit = st.text_input("Business Unit")
            new_manager = st.text_input("Manager")
            new_region = st.text_input("Region")
        
        submitted = st.form_submit_button("Add Champion", type="primary")
        
        if submitted:
            if not new_name or not new_department or not new_location or not new_email or not new_role:
                st.error("Please fill in all required fields (marked with *).")
            else:
                # Check if location can be geocoded
                coords = geocode_location(new_location)
                
                db.add_champion(
                    project_id=project_id,
                    champion_name=new_name,
                    department=new_department,
                    location=new_location,
                    email=new_email,
                    role=new_role,
                    business_unit=new_business_unit if new_business_unit else None,
                    manager=new_manager if new_manager else None,
                    region=new_region if new_region else None
                )
                
                if coords["resolved"]:
                    st.success(f"✅ Champion {new_name} added successfully! Location mapped to coordinates.")
                else:
                    st.success(f"✅ Champion {new_name} added successfully!")
                    st.warning(f"⚠️ Location '{new_location}' could not be automatically mapped. The champion will not appear on the Location Insights map until coordinates are available.")
                
                st.rerun()
    

def render_observations_tab(project_id, project):
    """Observations tab - View and filter observations"""
    st.subheader("Observation History")
    
    observations_df = db.get_observations_by_project(project_id)
    
    if len(observations_df) == 0:
        st.info("No observations yet. Champions can submit observations from the Submit Field Observation page.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        departments = ['All'] + sorted(observations_df['department'].unique().tolist())
        selected_dept = st.selectbox("Filter by Department", departments)
    
    with col2:
        statuses = ['All'] + ['Green', 'Yellow', 'Red']
        selected_status = st.selectbox("Filter by Status", statuses)
    
    with col3:
        date_range = st.selectbox("Date Range", ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"])
    
    # Apply filters
    filtered_df = observations_df.copy()
    
    if selected_dept != 'All':
        filtered_df = filtered_df[filtered_df['department'] == selected_dept]
    
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['overall_status'] == selected_status]
    
    if date_range != "All Time":
        from datetime import timedelta
        days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
        cutoff = (datetime.now() - timedelta(days=days_map[date_range])).strftime("%Y-%m-%d")
        filtered_df = filtered_df[filtered_df['observation_date'] >= cutoff]
    
    st.markdown(f"**Showing {len(filtered_df)} of {len(observations_df)} observations**")
    
    # Display observations
    for _, obs in filtered_df.iterrows():
        with st.expander(f"{get_status_color(obs['overall_status'])} {obs['champion_name']} - {obs['department']} ({obs['observation_date'][:10]}) - Score: {obs['readiness_score']}/10"):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"**Champion:** {obs['champion_name']}")
                st.markdown(f"**Department:** {obs['department']}")
                if 'location' in obs and pd.notna(obs['location']):
                    st.markdown(f"**Location:** {obs['location']}")
                st.markdown(f"**Status:** {get_status_color(obs['overall_status'])} {obs['overall_status']}")
                st.markdown(f"**Readiness:** {obs['readiness_score']}/10")
                st.markdown(f"**Date:** {obs['observation_date'][:10]}")
            
            with col2:
                st.markdown("**What are you hearing?**")
                st.write(obs['what_are_you_hearing'])
                
                st.markdown("**Questions emerging?**")
                st.write(obs['questions_emerging'])
                
                st.markdown("**Leadership should know:**")
                st.write(obs['leadership_should_know'])

def render_executive_summary_tab(project_id, project):
    """Executive Summary tab"""
    
    latest_summary = db.get_latest_summary(project_id)
    
    if latest_summary:
        # Display summary in styled card
        st.markdown('<div class="executive-summary">', unsafe_allow_html=True)
        
        # Header with date
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("## Executive Summary")
        with col2:
            st.caption(f"Generated: {latest_summary['summary_date']}")
        
        st.markdown("---")
        
        # Summary content
        st.markdown(latest_summary['summary_text'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("📊 No executive summary generated yet. Click the button below to create one based on field observations.")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🤖 Generate Executive Summary", type="primary", use_container_width=True):
            observations_df = db.get_observations_by_project(project_id)
            
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

def render_initiative_settings_tab(project_id, project):
    """Initiative Settings tab - Edit initiative details"""
    st.subheader("Initiative Settings")
    
    STATUS_OPTIONS = ["Planning", "Active", "Go-Live", "Stabilization", "Complete", "On Hold"]
    
    with st.form("edit_initiative_workspace"):
        st.markdown("### Initiative Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Initiative Name *",
                value=project['project_name'],
                help="The official name of the change initiative"
            )
            
            sponsor_name = st.text_input(
                "Executive Sponsor *",
                value=project['sponsor_name'],
                help="Executive sponsor responsible for the change"
            )
            
            project_manager = st.text_input(
                "Project Manager",
                value=project.get('project_manager', ''),
                help="Project manager leading execution"
            )
            
            change_lead = st.text_input(
                "Change Lead",
                value=project.get('change_lead', ''),
                help="Change management lead"
            )
        
        with col2:
            current_status = project['status']
            if current_status not in STATUS_OPTIONS:
                current_status = "Active"
            
            status = st.selectbox(
                "Status *",
                options=STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(current_status),
                help="Current initiative status"
            )
            
            start_date = st.date_input(
                "Start Date *",
                value=datetime.strptime(project['start_date'], "%Y-%m-%d").date() if project['start_date'] else datetime.now().date(),
                help="Initiative start date"
            )
            
            go_live_date = st.date_input(
                "Go-Live Date",
                value=datetime.strptime(project['go_live_date'], "%Y-%m-%d").date() if project.get('go_live_date') else None,
                help="Planned go-live date"
            )
            
            end_date = st.date_input(
                "End Date",
                value=datetime.strptime(project['end_date'], "%Y-%m-%d").date() if project.get('end_date') else None,
                help="Project completion date"
            )
        
        project_description = st.text_area(
            "Project Description",
            value=project.get('project_description', ''),
            height=100,
            help="Brief description of the change initiative and its objectives"
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
        
        if submitted:
            if not project_name or not sponsor_name or not start_date:
                st.error("Please fill in all required fields (marked with *).")
            else:
                db.update_project(
                    project_id=project_id,
                    project_name=project_name,
                    project_description=project_description,
                    sponsor_name=sponsor_name,
                    project_manager=project_manager,
                    change_lead=change_lead,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    go_live_date=go_live_date.strftime("%Y-%m-%d") if go_live_date else None,
                    end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
                    status=status
                )
                
                st.success(f"✅ Project '{project_name}' updated successfully!")
                st.rerun()

def get_status_color(status):
    """Get colored emoji for status"""
    colors = {
        "Green": "🟢",
        "Yellow": "🟡",
        "Red": "🔴",
        "Planning": "🔵",
        "Active": "🟢",
        "Go-Live": "🟡",
        "Stabilization": "🟠",
        "Complete": "✅",
        "On Hold": "⏸️"
    }
    return colors.get(status, "⚪")
