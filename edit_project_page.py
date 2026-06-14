import streamlit as st
import database as db
from datetime import datetime

def edit_project_page():
    """Page: Edit Project"""
    st.markdown('<p class="main-header">✏️ Edit Project</p>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Update project details and settings.</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Check if project_id is in session state
    if 'edit_project_id' not in st.session_state:
        st.warning("No project selected for editing. Please select a project from the Change Manager Dashboard.")
        if st.button("Go to Change Manager Dashboard"):
            st.session_state.current_page = "Change Manager Dashboard"
            st.rerun()
        return
    
    project_id = st.session_state.edit_project_id
    project = db.get_project_by_id(project_id)
    
    if not project:
        st.error("Project not found.")
        return
    
    st.subheader(f"Editing: {project['project_name']}")
    
    # Define status options
    STATUS_OPTIONS = ["Planning", "Active", "Go-Live", "Stabilization", "Complete", "On Hold"]
    
    with st.form("edit_project_form"):
        st.markdown("### Project Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Project Name *",
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
                help="Current project status"
            )
            
            start_date = st.date_input(
                "Start Date *",
                value=datetime.strptime(project['start_date'], "%Y-%m-%d").date() if project['start_date'] else datetime.now().date(),
                help="Project start date"
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
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
        
        with col2:
            cancel = st.form_submit_button("Cancel")
        
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
                
                # Clear the edit session state
                if 'edit_project_id' in st.session_state:
                    del st.session_state.edit_project_id
                
                st.info("Returning to Change Manager Dashboard...")
                st.session_state.current_page = "Change Manager Dashboard"
                st.rerun()
        
        if cancel:
            if 'edit_project_id' in st.session_state:
                del st.session_state.edit_project_id
            st.session_state.current_page = "Change Manager Dashboard"
            st.rerun()
