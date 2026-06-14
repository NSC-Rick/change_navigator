import streamlit as st
import database as db

def render_champion_edit_interface(project_id, champions_df):
    """Render champion edit/delete interface"""
    
    if len(champions_df) == 0:
        return
    
    st.markdown("---")
    st.subheader("Edit or Delete Champion")
    
    # Select champion to edit
    champion_names = champions_df['champion_name'].tolist()
    champion_ids = champions_df['id'].tolist()
    
    champion_options = [f"{name} ({champions_df[champions_df['id'] == cid]['department'].iloc[0]})" 
                       for name, cid in zip(champion_names, champion_ids)]
    
    selected_champion_display = st.selectbox(
        "Select Champion to Edit/Delete",
        options=champion_options,
        key=f"edit_champion_select_{project_id}"
    )
    
    if selected_champion_display:
        selected_index = champion_options.index(selected_champion_display)
        selected_champion_id = champion_ids[selected_index]
        selected_champion = champions_df[champions_df['id'] == selected_champion_id].iloc[0]
        
        # Edit form
        with st.form(f"edit_champion_form_{selected_champion_id}"):
            st.markdown(f"**Editing: {selected_champion['champion_name']}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                edit_name = st.text_input(
                    "Champion Name *",
                    value=selected_champion['champion_name']
                )
                edit_department = st.text_input(
                    "Department *",
                    value=selected_champion['department']
                )
                edit_location = st.text_input(
                    "Location *",
                    value=selected_champion['location'] if selected_champion['location'] else ""
                )
                edit_email = st.text_input(
                    "Email *",
                    value=selected_champion['email']
                )
            
            with col2:
                edit_role = st.text_input(
                    "Role *",
                    value=selected_champion['role']
                )
                edit_business_unit = st.text_input(
                    "Business Unit",
                    value=selected_champion['business_unit'] if selected_champion.get('business_unit') else ""
                )
                edit_manager = st.text_input(
                    "Manager",
                    value=selected_champion['manager'] if selected_champion.get('manager') else ""
                )
                edit_region = st.text_input(
                    "Region",
                    value=selected_champion['region'] if selected_champion.get('region') else ""
                )
            
            col_save, col_delete = st.columns([1, 1])
            
            with col_save:
                save_button = st.form_submit_button("💾 Save Changes", type="primary")
            
            with col_delete:
                delete_button = st.form_submit_button("🗑️ Delete Champion", type="secondary")
            
            if save_button:
                if not edit_name or not edit_department or not edit_location or not edit_email or not edit_role:
                    st.error("Please fill in all required fields (marked with *).")
                else:
                    success = db.update_champion(
                        champion_id=selected_champion_id,
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
                        st.success(f"✅ Champion '{edit_name}' updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update champion. Please try again.")
            
            if delete_button:
                # Check if champion has observations
                if selected_champion['observation_count'] > 0:
                    st.error(
                        f"⚠️ Cannot delete champion '{selected_champion['champion_name']}' "
                        f"because they have {int(selected_champion['observation_count'])} observation(s). "
                        "Please delete or reassign their observations first."
                    )
                else:
                    success = db.delete_champion(selected_champion_id)
                    if success:
                        st.success(f"✅ Champion '{selected_champion['champion_name']}' deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete champion. Please try again.")
