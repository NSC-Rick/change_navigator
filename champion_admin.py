"""
Champion Administration - Manage change champions under Administration
"""
import streamlit as st
import pandas as pd
import database as db
from geocoding import geocode_location

def render_champion_administration():
    """Champion Administration - Add, Edit, Delete champions"""
    st.subheader("Change Champion Management")
    st.caption("Manage change champions across all initiatives")
    
    # Get all projects for champion assignment
    projects_df = db.get_all_projects()
    
    if len(projects_df) == 0:
        st.info("No initiatives found. Please create an initiative first.")
        return
    
    # Project selector
    project_options = [f"{row['project_name']}" for _, row in projects_df.iterrows()]
    selected_project_display = st.selectbox("Select Initiative", project_options)
    
    if selected_project_display:
        selected_index = project_options.index(selected_project_display)
        selected_project = projects_df.iloc[selected_index]
        project_id = selected_project['id']
        
        # Get champions for selected project
        champions_df = db.get_champions_by_project(project_id)
        
        st.markdown("---")
        
        # Display existing champions
        st.markdown("### Current Champions")
        
        if len(champions_df) == 0:
            st.info("No champions assigned to this initiative yet.")
        else:
            # Display champions table
            display_df = champions_df[['champion_name', 'department', 'location', 'email', 'role']].copy()
            display_df.columns = ['Name', 'Department', 'Location', 'Email', 'Role']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            st.caption(f"Total Champions: {len(champions_df)}")
        
        st.markdown("---")
        
        # Add New Champion
        with st.expander("➕ Add New Champion", expanded=False):
            with st.form("add_champion_admin"):
                st.markdown("**Add New Champion**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name = st.text_input("Champion Name *", key="new_champ_name")
                    new_department = st.text_input("Department *", key="new_champ_dept")
                    new_location = st.text_input("Location *", placeholder="e.g., New York, NY", key="new_champ_loc")
                    new_email = st.text_input("Email *", key="new_champ_email")
                
                with col2:
                    new_role = st.text_input("Role *", key="new_champ_role")
                    new_business_unit = st.text_input("Business Unit", key="new_champ_bu")
                    new_manager = st.text_input("Manager", key="new_champ_mgr")
                    new_region = st.text_input("Region", key="new_champ_region")
                
                submitted = st.form_submit_button("Add Champion", type="primary", use_container_width=True)
                
                if submitted:
                    if new_name and new_department and new_location and new_email and new_role:
                        try:
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
                            st.success(f"✅ Champion '{new_name}' added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding champion: {e}")
                    else:
                        st.error("Please fill in all required fields (marked with *).")
        
        # Edit/Delete Champions
        if len(champions_df) > 0:
            with st.expander("✏️ Edit or Delete Champion", expanded=False):
                # Champion selector
                champion_options = [f"{row['champion_name']} - {row['department']}" for _, row in champions_df.iterrows()]
                selected_champion_display = st.selectbox(
                    "Select Champion",
                    options=champion_options,
                    key="edit_champion_select"
                )
                
                if selected_champion_display:
                    selected_index = champion_options.index(selected_champion_display)
                    selected_champion = champions_df.iloc[selected_index]
                    champion_id = selected_champion['id']
                    
                    # Edit form
                    with st.form(f"edit_champion_form_{champion_id}"):
                        st.markdown(f"**Editing: {selected_champion['champion_name']}**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("Champion Name *", value=selected_champion['champion_name'])
                            edit_department = st.text_input("Department *", value=selected_champion['department'])
                            edit_location = st.text_input("Location *", value=selected_champion['location'])
                            edit_email = st.text_input("Email *", value=selected_champion['email'])
                        
                        with col2:
                            edit_role = st.text_input("Role *", value=selected_champion['role'])
                            edit_business_unit = st.text_input("Business Unit", value=selected_champion.get('business_unit', '') or '')
                            edit_manager = st.text_input("Manager", value=selected_champion.get('manager', '') or '')
                            edit_region = st.text_input("Region", value=selected_champion.get('region', '') or '')
                        
                        update_submitted = st.form_submit_button("Update Champion", type="primary", use_container_width=True)
                        
                        if update_submitted:
                            if edit_name and edit_department and edit_location and edit_email and edit_role:
                                try:
                                    db.update_champion(
                                        champion_id=champion_id,
                                        champion_name=edit_name,
                                        department=edit_department,
                                        location=edit_location,
                                        email=edit_email,
                                        role=edit_role,
                                        business_unit=edit_business_unit if edit_business_unit else None,
                                        manager=edit_manager if edit_manager else None,
                                        region=edit_region if edit_region else None
                                    )
                                    st.success(f"✅ Champion '{edit_name}' updated successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating champion: {e}")
                            else:
                                st.error("Please fill in all required fields (marked with *).")
                    
                    st.markdown("---")
                    
                    # Delete champion
                    st.markdown("**Delete Champion**")
                    st.warning("⚠️ Champions with observations cannot be deleted. Delete or reassign observations first.")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f"🗑️ Delete '{selected_champion['champion_name']}'", type="secondary", use_container_width=True):
                            # Check if champion has observations
                            observations_df = db.get_observations_by_project(project_id)
                            champion_obs = observations_df[observations_df['champion_id'] == champion_id] if len(observations_df) > 0 else pd.DataFrame()
                            
                            if len(champion_obs) > 0:
                                st.error(
                                    f"❌ Cannot delete champion '{selected_champion['champion_name']}'. "
                                    f"They have {len(champion_obs)} observation(s). "
                                    "Please delete or reassign their observations first."
                                )
                            else:
                                success = db.delete_champion(champion_id)
                                if success:
                                    st.success(f"✅ Champion '{selected_champion['champion_name']}' deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete champion.")
