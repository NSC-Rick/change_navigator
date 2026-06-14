import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db
from datetime import datetime
import seed_data
from project_workspace_page import initiative_workspace_page
from champion_admin import render_champion_administration
from summary_utils import generate_placeholder_summary

# DEBUG: Log database file being used
st.sidebar.caption(f"🗄️ DB: {db.DATABASE_NAME}")

st.set_page_config(
    page_title="North Star Change Navigator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Enterprise Dashboard Styling */
    
    /* Main App Background - Light */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Sidebar - Navy Blue */
    [data-testid="stSidebar"] {
        background-color: #1e3a5f;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        color: #ffffff !important;
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Logo/Header in Sidebar */
    [data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        padding: 1rem 0;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1.5rem;
    }
    
    /* Dashboard Cards */
    .dashboard-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    }
    
    .project-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .project-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .summary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background-color: #ffffff;
        padding: 1.25rem;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    /* Typography */
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }
    
    .tagline {
        font-size: 1rem;
        color: #6c757d;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e3a5f;
        margin-bottom: 1rem;
    }
    
    .card-subtitle {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 0.5rem;
    }
    
    /* Status Colors */
    .status-green {
        color: #28a745;
        font-weight: 600;
    }
    
    .status-yellow {
        color: #ffc107;
        font-weight: 600;
    }
    
    .status-red {
        color: #dc3545;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        border: 1px solid #e9ecef;
        border-bottom: none;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1e3a5f;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    
    /* Executive Summary Card */
    .executive-summary {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
    }
    
    .executive-summary h2 {
        color: #1e3a5f;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .executive-summary h3 {
        color: #495057;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Field Observation Form */
    .observation-form {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    .status-button {
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 2px solid transparent;
    }
    
    .status-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .status-good {
        background-color: #d4edda;
        color: #155724;
        border-color: #28a745;
    }
    
    .status-mixed {
        background-color: #fff3cd;
        color: #856404;
        border-color: #ffc107;
    }
    
    .status-concerned {
        background-color: #f8d7da;
        color: #721c24;
        border-color: #dc3545;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Spacing */
    .element-container {
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def render_header():
    """Render the main header"""
    st.markdown('<p class="main-header">🧭 North Star Change Navigator</p>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Turning field observations into organizational intelligence.</p>', unsafe_allow_html=True)
    st.markdown("---")

def get_status_color(status):
    """Get color for status indicator"""
    if status == "Green":
        return "🟢"
    elif status == "Yellow":
        return "🟡"
    elif status == "Red":
        return "🔴"
    return "⚪"

def get_readiness_color(score):
    """Get color based on readiness score"""
    if score is None or pd.isna(score):
        return "⚪"
    if score >= 8:
        return "🟢"
    elif score >= 6:
        return "🟡"
    else:
        return "🔴"

def change_manager_dashboard():
    """Change Manager Dashboard - Landing page showing what needs attention"""
    render_header()
    
    projects_df = db.get_all_projects()
    
    if len(projects_df) == 0:
        st.warning("No initiatives found. Please load sample data from the Administration page.")
        return
    
    # Dashboard summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Active Initiatives", len(projects_df))
    
    with col2:
        total_champions = projects_df['champion_count'].sum()
        st.metric("👥 Total Champions", int(total_champions))
    
    with col3:
        total_obs = projects_df['observation_count'].sum()
        st.metric("📝 Field Observations", int(total_obs))
    
    with col4:
        avg_readiness = projects_df['avg_readiness_score'].mean()
        if pd.notna(avg_readiness):
            st.metric("📊 Overall Readiness", f"{avg_readiness:.1f}/10")
        else:
            st.metric("📊 Overall Readiness", "N/A")
    
    st.markdown("---")
    st.subheader("🎯 Your Initiatives")
    
    # Display projects as cards in a grid
    cols_per_row = 2
    for i in range(0, len(projects_df), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(projects_df):
                project = projects_df.iloc[i + j]
                
                with col:
                    # Project card
                    card_html = f"""
                    <div class="project-card">
                        <h3 style="color: #1e3a5f; margin-bottom: 0.5rem; font-size: 1.25rem;">
                            {project['project_name']}
                        </h3>
                        <p style="color: #6c757d; font-size: 0.9rem; margin-bottom: 1rem;">
                            {project.get('client_name', 'N/A')} | {project['sponsor_name']}
                        </p>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # Metrics in columns
                    mcol1, mcol2, mcol3 = st.columns(3)
                    
                    with mcol1:
                        st.metric("👥 Champions", int(project['champion_count']))
                    
                    with mcol2:
                        st.metric("📝 Observations", int(project['observation_count']))
                    
                    with mcol3:
                        readiness = project['avg_readiness_score']
                        if pd.notna(readiness):
                            st.metric("🎯 Readiness", f"{readiness:.1f}")
                        else:
                            st.metric("🎯 Readiness", "N/A")
                    
                    # Status badge
                    status_color = "#28a745" if project['status'] == "Active" else "#6c757d"
                    st.markdown(f"<span style='background-color: {status_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 500;'>{project['status']}</span>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)

def submit_observation():
    """Page 3: Submit Field Observation"""
    render_header()
    
    projects_df = db.get_all_projects()
    
    if len(projects_df) == 0:
        st.warning("No initiatives found. Please load sample data from the Administration page.")
        return
    
    # Form container
    st.markdown('<div class="observation-form">', unsafe_allow_html=True)
    
    st.markdown("### 📋 Weekly Field Report")
    st.caption("Share what you're seeing and hearing in the field. Takes about 2 minutes.")
    
    st.markdown("---")
    
    # Initiative and Champion selection
    col1, col2 = st.columns(2)
    
    with col1:
        project_names = projects_df['project_name'].tolist()
        selected_project_name = st.selectbox("🎯 Initiative", project_names, key="obs_project")
    
    selected_project = projects_df[projects_df['project_name'] == selected_project_name].iloc[0]
    project_id = selected_project['id']
    
    champions_df = db.get_champions_by_project(project_id)
    
    if len(champions_df) == 0:
        st.warning("No champions found for this initiative. Please add champions first.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Display champion with location if available
    if 'location' in champions_df.columns:
        champion_display = champions_df.apply(
            lambda x: f"{x['champion_name']} ({x['department']}, {x['location']})", axis=1
        ).tolist()
    else:
        champion_display = champions_df.apply(
            lambda x: f"{x['champion_name']} ({x['department']})", axis=1
        ).tolist()
    
    champion_names = champions_df['champion_name'].tolist()
    
    with col2:
        selected_champion_display = st.selectbox("👤 Your Name", champion_display)
    
    selected_champion_index = champion_display.index(selected_champion_display)
    selected_champion_name = champion_names[selected_champion_index]
    
    selected_champion = champions_df[champions_df['champion_name'] == selected_champion_name].iloc[0]
    champion_id = selected_champion['id']
    
    st.markdown("---")
    
    # Overall sentiment with large buttons
    st.markdown("#### How are things going?")
    
    col1, col2, col3 = st.columns(3)
    
    # Initialize session state for status if not exists
    if 'selected_status' not in st.session_state:
        st.session_state.selected_status = "Mixed"
    
    with col1:
        if st.button("✅ Good", key="status_good", use_container_width=True, type="primary" if st.session_state.selected_status == "Green" else "secondary"):
            st.session_state.selected_status = "Green"
            st.rerun()
    
    with col2:
        if st.button("⚠️ Mixed", key="status_mixed", use_container_width=True, type="primary" if st.session_state.selected_status == "Yellow" else "secondary"):
            st.session_state.selected_status = "Yellow"
            st.rerun()
    
    with col3:
        if st.button("🚨 Concerned", key="status_concerned", use_container_width=True, type="primary" if st.session_state.selected_status == "Red" else "secondary"):
            st.session_state.selected_status = "Red"
            st.rerun()
    
    overall_status = st.session_state.selected_status
    
    st.markdown("---")
    
    # Readiness slider
    st.markdown("#### Readiness Level")
    readiness_score = st.slider(
        "How ready is your area for this change?",
        min_value=1,
        max_value=10,
        value=7,
        help="1 = Not ready at all, 10 = Fully ready"
    )
    
    st.markdown("---")
    
    # Simplified text areas
    st.markdown("#### What are you hearing?")
    what_hearing = st.text_area(
        "Share feedback, concerns, or reactions from the field",
        height=120,
        placeholder="What are people saying about this change?",
        label_visibility="collapsed"
    )
    
    st.markdown("#### Key message for leadership")
    leadership_know = st.text_area(
        "What should leadership know right now?",
        height=120,
        placeholder="Insights, risks, or opportunities that need attention",
        label_visibility="collapsed"
    )
    
    # Set questions to a default value for simplified form
    questions = what_hearing  # Combine into single field for simplicity
    
    if st.button("Submit Observation", type="primary"):
        if not what_hearing or not questions or not leadership_know:
            st.error("Please fill in all fields before submitting.")
        else:
            # DEBUG: Log submission attempt
            st.write("🔍 DEBUG: Entering add_observation")
            st.write(f"Project ID: {project_id}")
            st.write(f"Champion ID: {champion_id}")
            st.write(f"Status: {overall_status}")
            st.write(f"Readiness: {readiness_score}")
            
            observation_id = db.add_observation(
                project_id=int(project_id),
                champion_id=int(champion_id),
                overall_status=overall_status,
                readiness_score=readiness_score,
                what_are_you_hearing=what_hearing,
                questions_emerging=questions,
                leadership_should_know=leadership_know
            )
            
            # DEBUG: Verify observation was saved
            st.write(f"✅ Observation ID returned: {observation_id}")
            
            # Verify record exists in database
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM observations")
            total_obs = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM observations WHERE project_id = ?", (project_id,))
            project_obs = cursor.fetchone()[0]
            conn.close()
            
            st.write(f"📊 Total observations in DB: {total_obs}")
            st.write(f"📊 Observations for this project: {project_obs}")
            
            st.success("✅ Field observation submitted successfully!")
            st.info("🔄 Refresh the page or navigate to Initiative Workspace to see the new observation.")
            st.balloons()
            st.info("Your observation has been recorded and will be included in the next executive summary.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def admin_page():
    """Page 6: Admin / Seed Data"""
    render_header()
    st.header("⚙️ Administration")
    
    # Tabs for different admin sections
    admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
        "🎯 Initiative Administration",
        "👥 Change Champions",
        "🗄️ Database Management",
        "🔍 Data Integrity"
    ])
    
    with admin_tab1:
        render_project_administration()
    
    with admin_tab2:
        render_champion_administration()
    
    with admin_tab3:
        render_database_management()
    
    with admin_tab4:
        render_data_integrity_check()

def render_project_administration():
    """Initiative Administration - Add, Edit, Archive, Delete initiatives"""
    st.subheader("Initiative Administration")
    
    # Get all initiatives including archived
    all_projects = db.get_all_projects(include_archived=True)
    
    # Add New Initiative Section
    with st.expander("➕ Add New Initiative", expanded=False):
        with st.form("add_project_form"):
            st.markdown("### Create New Initiative")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_project_name = st.text_input("Initiative Name *", help="Official name of the change initiative")
                new_client_name = st.text_input("Client Name", help="Client or organization name")
                new_sponsor = st.text_input("Executive Sponsor *", help="Executive sponsor responsible for the change")
                new_pm = st.text_input("Project Manager", help="Project manager leading execution")
                new_change_lead = st.text_input("Change Lead", help="Change management lead")
                new_business_unit = st.text_input("Business Unit", help="Business unit or division")
            
            with col2:
                new_status = st.selectbox("Status *", ["Planning", "Active", "Go-Live", "Stabilization", "Complete", "On Hold"])
                new_start_date = st.date_input("Start Date *")
                new_go_live = st.date_input("Go-Live Date")
                new_end_date = st.date_input("End Date")
            
            new_description = st.text_area("Initiative Description", height=100, help="Brief description of the change initiative")
            
            submitted = st.form_submit_button("Create Initiative", type="primary", use_container_width=True)
            
            if submitted:
                if not new_project_name or not new_sponsor:
                    st.error("Please fill in all required fields (marked with *).")
                else:
                    db.add_project(
                        project_name=new_project_name,
                        client_name=new_client_name if new_client_name else None,
                        project_description=new_description if new_description else None,
                        sponsor_name=new_sponsor,
                        project_manager=new_pm if new_pm else None,
                        change_lead=new_change_lead if new_change_lead else None,
                        start_date=str(new_start_date),
                        go_live_date=str(new_go_live) if new_go_live else None,
                        end_date=str(new_end_date) if new_end_date else None,
                        status=new_status,
                        business_unit=new_business_unit if new_business_unit else None
                    )
                    st.success(f"✅ Initiative '{new_project_name}' created successfully!")
                    st.rerun()
    
    st.markdown("---")
    
    # Manage Existing Initiatives
    st.markdown("### Manage Existing Initiatives")
    
    if len(all_projects) == 0:
        st.info("No initiatives found. Create your first initiative above.")
        return
    
    # Initiative selector
    project_options = [f"{row['project_name']} ({row['status']})" for _, row in all_projects.iterrows()]
    selected_project_display = st.selectbox("Select Initiative to Manage", project_options)
    
    if selected_project_display:
        selected_index = project_options.index(selected_project_display)
        selected_project = all_projects.iloc[selected_index]
        project_id = selected_project['id']
        
        # Edit Initiative Section
        with st.expander("✏️ Edit Initiative", expanded=True):
            with st.form(f"edit_project_{project_id}"):
                st.markdown("### Edit Initiative Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Initiative Name *", value=selected_project['project_name'])
                    edit_client = st.text_input("Client Name", value=selected_project.get('client_name', '') or '')
                    edit_sponsor = st.text_input("Executive Sponsor *", value=selected_project['sponsor_name'])
                    edit_pm = st.text_input("Project Manager", value=selected_project.get('project_manager', '') or '')
                    edit_change_lead = st.text_input("Change Lead", value=selected_project.get('change_lead', '') or '')
                    edit_business_unit = st.text_input("Business Unit", value=selected_project.get('business_unit', '') or '')
                
                with col2:
                    STATUS_OPTIONS = ["Planning", "Active", "Go-Live", "Stabilization", "Complete", "On Hold", "Archived"]
                    current_status_index = STATUS_OPTIONS.index(selected_project['status']) if selected_project['status'] in STATUS_OPTIONS else 0
                    edit_status = st.selectbox("Status *", STATUS_OPTIONS, index=current_status_index)
                    
                    edit_start = st.date_input("Start Date *", value=pd.to_datetime(selected_project['start_date']).date() if pd.notna(selected_project['start_date']) else None)
                    edit_go_live = st.date_input("Go-Live Date", value=pd.to_datetime(selected_project['go_live_date']).date() if pd.notna(selected_project.get('go_live_date')) else None)
                    edit_end = st.date_input("End Date", value=pd.to_datetime(selected_project['end_date']).date() if pd.notna(selected_project['end_date']) else None)
                
                edit_desc = st.text_area("Initiative Description", value=selected_project.get('project_description', '') or '', height=100)
                
                update_submitted = st.form_submit_button("Update Initiative", type="primary", use_container_width=True)
                
                if update_submitted:
                    if not edit_name or not edit_sponsor:
                        st.error("Please fill in all required fields (marked with *).")
                    else:
                        db.update_project(
                            project_id=project_id,
                            project_name=edit_name,
                            client_name=edit_client if edit_client else None,
                            project_description=edit_desc if edit_desc else None,
                            sponsor_name=edit_sponsor,
                            project_manager=edit_pm if edit_pm else None,
                            change_lead=edit_change_lead if edit_change_lead else None,
                            start_date=str(edit_start),
                            go_live_date=str(edit_go_live) if edit_go_live else None,
                            end_date=str(edit_end) if edit_end else None,
                            status=edit_status,
                            business_unit=edit_business_unit if edit_business_unit else None
                        )
                        st.success(f"✅ Initiative '{edit_name}' updated successfully!")
                        st.rerun()
        
        # Archive/Delete Section
        st.markdown("---")
        st.markdown("### Initiative Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if selected_project['status'] != 'Archived':
                st.markdown("**Archive Initiative**")
                st.caption("Archive this initiative to hide it from active views. Data is preserved.")
                if st.button("📦 Archive Initiative", key=f"archive_{project_id}", use_container_width=True):
                    db.archive_project(project_id)
                    st.success(f"✅ Initiative '{selected_project['project_name']}' archived successfully!")
                    st.rerun()
            else:
                st.info("This initiative is already archived.")
        
        with col2:
            st.markdown("**Delete Initiative**")
            st.caption("⚠️ Permanently delete this initiative and ALL associated data (champions, observations, summaries).")
            
            # Initialize session state for delete confirmation
            if f'delete_confirm_{project_id}' not in st.session_state:
                st.session_state[f'delete_confirm_{project_id}'] = False
            
            if not st.session_state[f'delete_confirm_{project_id}']:
                if st.button("🗑️ Delete Initiative", key=f"delete_btn_{project_id}", use_container_width=True):
                    st.session_state[f'delete_confirm_{project_id}'] = True
                    st.rerun()
            else:
                st.warning("⚠️ **This action cannot be undone!**")
                confirm_text = st.text_input(f"Type DELETE to confirm deletion of '{selected_project['project_name']}':", key=f"confirm_text_{project_id}")
                
                col_confirm1, col_confirm2 = st.columns(2)
                with col_confirm1:
                    if st.button("Cancel", key=f"cancel_{project_id}", use_container_width=True):
                        st.session_state[f'delete_confirm_{project_id}'] = False
                        st.rerun()
                
                with col_confirm2:
                    if st.button("Confirm Delete", key=f"confirm_delete_{project_id}", type="primary", use_container_width=True):
                        if confirm_text == "DELETE":
                            db.delete_project(project_id)
                            st.success(f"✅ Initiative '{selected_project['project_name']}' deleted successfully!")
                            st.session_state[f'delete_confirm_{project_id}'] = False
                            st.rerun()
                        else:
                            st.error("Please type DELETE exactly to confirm.")

def render_database_management():
    """Database Management - Initialize and Load Sample Data"""
    st.subheader("Database Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Initialize Database")
        st.caption("Create database tables (safe to run multiple times)")
        if st.button("Initialize Database", type="secondary"):
            db.init_database()
            st.success("✅ Database initialized successfully!")
    
    with col2:
        st.markdown("### Load Sample Data")
        st.caption("Load demo data with 3 projects, 12 champions, and 30 observations")
        st.info("💡 This will clear all existing data first")
        if st.button("Load Sample Data", type="primary"):
            with st.spinner("Clearing existing data..."):
                db.clear_all_data()
            with st.spinner("Loading sample data..."):
                seed_data.seed_sample_data()
            st.success("✅ Sample data loaded successfully!")
            st.info("Navigate to Change Manager Dashboard to see the demo data.")
    
    with col3:
        st.markdown("### Geocode Champions")
        st.caption("Populate coordinates for champions with missing location data")
        if st.button("🌍 Geocode Locations", type="secondary"):
            from migrate_champion_coordinates import migrate_champion_coordinates
            with st.spinner("Geocoding champion locations..."):
                stats = migrate_champion_coordinates(verbose=False)
            
            if stats["successfully_geocoded"] > 0:
                st.success(f"✅ Successfully geocoded {stats['successfully_geocoded']} champion(s)!")
            
            if stats["failed_geocoding"] > 0:
                st.warning(f"⚠️ {stats['failed_geocoding']} champion(s) could not be geocoded.")
                with st.expander("View failed locations"):
                    for detail in stats["details"]:
                        if detail["status"] == "failed_geocoding":
                            st.write(f"• {detail['name']}: '{detail['location']}'")
                    st.info("💡 Edit champion locations to use recognized format (e.g., 'Boston, MA')")
            
            if stats["total_champions"] == 0:
                st.info("All champions already have coordinates!")

def render_data_integrity_check():
    """Data Integrity Check"""
    st.subheader("Data Integrity Check")
    
    if st.button("🔍 Diagnose Data Issues", type="secondary"):
        issues = db.diagnose_data_integrity()
        if issues:
            st.error("⚠️ Data integrity issues found:")
            for issue in issues:
                st.write(f"- {issue}")
            st.warning("**Recommendation:** Reload sample data to fix these issues.")
        else:
            st.success("✅ No data integrity issues found!")
    
    st.markdown("---")
    
    st.subheader("Database Statistics")
    
    try:
        projects_df = db.get_all_projects()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Projects", len(projects_df))
        
        with col2:
            total_champions = projects_df['champion_count'].sum() if len(projects_df) > 0 else 0
            st.metric("Champions", int(total_champions))
        
        with col3:
            total_observations = projects_df['observation_count'].sum() if len(projects_df) > 0 else 0
            st.metric("Observations", int(total_observations))
        
        with col4:
            conn = db.get_connection()
            summary_count = pd.read_sql_query("SELECT COUNT(*) as count FROM ai_summaries", conn)
            conn.close()
            st.metric("AI Summaries", int(summary_count.iloc[0]['count']))
        
    except Exception as e:
        st.warning("Database not initialized yet. Click 'Initialize Database' to get started.")

def main():
    """Main application"""
    
    db.init_database()
    
    # Auto-select project if exactly one exists (single-project mode)
    # This eliminates the need to visit Change Manager Dashboard before accessing Initiative Workspace
    if 'active_project_id' not in st.session_state:
        try:
            projects_df = db.get_all_projects()
            if len(projects_df) == 1:
                # Automatically select the single project
                project = projects_df.iloc[0]
                st.session_state.active_project_id = project['id']
                st.session_state.active_project_name = project['project_name']
        except Exception:
            # Database not initialized yet, skip auto-selection
            pass
    
    # Sidebar branding
    st.sidebar.markdown("# 🧭 North Star")
    st.sidebar.markdown("### Change Navigator")
    st.sidebar.markdown("---")
    
    # Initialize session state for page if not exists
    # Support both old 'page' and new 'current_page' keys
    if 'current_page' not in st.session_state:
        if 'page' in st.session_state:
            # Migrate old key to new key
            page_map = {
                "📊 Portfolio View": "Change Manager Dashboard",
                "📋 Project Workspace": "Initiative Workspace",
                "📝 Submit Field Observation": "Submit Field Observation",
                "⚙️ Admin / Seed Data": "Administration"
            }
            st.session_state.current_page = page_map.get(st.session_state.page, "Change Manager Dashboard")
        else:
            st.session_state.current_page = "Change Manager Dashboard"
    
    # Normalize legacy page names to new names
    legacy_page_map = {
        "Portfolio View": "Change Manager Dashboard",
        "Project Workspace": "Initiative Workspace",
        "Admin / Seed Data": "Administration",
        "📊 Portfolio View": "Change Manager Dashboard",
        "📋 Project Workspace": "Initiative Workspace",
        "⚙️ Admin / Seed Data": "Administration"
    }
    if st.session_state.current_page in legacy_page_map:
        st.session_state.current_page = legacy_page_map[st.session_state.current_page]
    
    # Define navigation pages (display with emojis)
    nav_pages_display = [
        "🎯 Change Manager Dashboard",
        "📋 Initiative Workspace",
        "📝 Submit Field Observation",
        "⚙️ Administration"
    ]
    
    # Internal page names (without emojis)
    nav_pages_internal = [
        "Change Manager Dashboard",
        "Initiative Workspace",
        "Submit Field Observation",
        "Administration"
    ]
    
    # Check if programmatic navigation is in progress
    nav_in_progress = st.session_state.get('navigation_in_progress', False)
    
    # Map current_page to display name (only current pages, not legacy)
    page_to_display = {
        "Change Manager Dashboard": "🎯 Change Manager Dashboard",
        "Initiative Workspace": "📋 Initiative Workspace",
        "Submit Field Observation": "📝 Submit Field Observation",
        "Administration": "⚙️ Administration"
    }
    
    # Reverse mapping: display name to internal page name
    display_to_page = {
        "🎯 Change Manager Dashboard": "Change Manager Dashboard",
        "📋 Initiative Workspace": "Initiative Workspace",
        "📝 Submit Field Observation": "Submit Field Observation",
        "⚙️ Administration": "Administration"
    }
    
    # Get current display value - current_page is the single source of truth
    current_display = page_to_display.get(st.session_state.current_page, "🎯 Change Manager Dashboard")
    current_index = nav_pages_display.index(current_display)
    
    # Use radio buttons for navigation
    # The index parameter ensures the radio reflects current_page state
    page_display = st.sidebar.radio(
        "Select Page",
        options=nav_pages_display,
        index=current_index,
        key="page_selector"
    )
    
    # Only update current_page if user actually changed the selection
    # AND we're not in programmatic navigation
    if not nav_in_progress:
        selected_page = display_to_page[page_display]
        # Only update if the user selected a different page
        if selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
    else:
        # Clear the flag after one rerun
        st.session_state.navigation_in_progress = False
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Turning field observations into organizational intelligence.")
    
    if st.session_state.current_page == "Change Manager Dashboard":
        change_manager_dashboard()
    elif st.session_state.current_page == "Initiative Workspace":
        initiative_workspace_page()
    elif st.session_state.current_page == "Submit Field Observation":
        submit_observation()
    elif st.session_state.current_page == "Administration":
        admin_page()
    else:
        st.error(f"❌ Invalid page: '{st.session_state.current_page}'")
        st.warning("This page name is not recognized. Please use the sidebar to navigate.")
        st.session_state.current_page = "Change Manager Dashboard"
        st.stop()

if __name__ == "__main__":
    main()
