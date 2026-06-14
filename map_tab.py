"""
Map Tab - Standalone geographic visualization of champion locations
"""
import streamlit as st
import pandas as pd
import database as db
from location_insights import render_location_map

def render_map_tab(project_id, project):
    """Map Tab - Geographic visualization of champion participation"""
    
    st.markdown("### 🗺️ Champion Location Map")
    st.caption("Geographic visualization of champion participation and readiness")
    
    # Get champions and observations data
    champions_df = db.get_champions_by_project(project_id)
    observations_df = db.get_observations_by_project(project_id)
    
    if len(champions_df) == 0:
        st.info("No champions assigned to this initiative yet. Add champions in the Settings page.")
        return
    
    # Check if location data exists
    if 'location' not in champions_df.columns or champions_df['location'].isna().all():
        st.warning("⚠️ Location data is not available for champions. Please add location information in the Settings page.")
        return
    
    # Check if coordinates are available
    has_coords = 'latitude' in champions_df.columns and 'longitude' in champions_df.columns
    if not has_coords:
        st.warning("⚠️ Geographic coordinates are not available. Database migration may be required.")
        return
    
    # Merge observations with champions to get location data
    if len(observations_df) > 0:
        observations_df = observations_df.merge(
            champions_df[['id', 'location']],
            left_on='champion_id',
            right_on='id',
            how='left',
            suffixes=('', '_champ')
        )
    
    # Calculate location statistics
    location_stats = []
    
    for location in champions_df['location'].dropna().unique():
        location_champions = champions_df[champions_df['location'] == location]
        champion_count = len(location_champions)
        
        # Calculate observation coverage
        if len(observations_df) > 0:
            location_obs = observations_df[observations_df['location'] == location]
            champions_with_obs = location_obs['champion_id'].nunique()
            coverage_pct = (champions_with_obs / champion_count * 100) if champion_count > 0 else 0
            avg_readiness = location_obs['readiness_score'].mean() if len(location_obs) > 0 else None
            obs_count = len(location_obs)
        else:
            coverage_pct = 0
            avg_readiness = None
            obs_count = 0
        
        # Get coordinates from stored champion data (use first champion's coordinates for this location)
        location_champ = location_champions.iloc[0]
        lat = location_champ.get('latitude')
        lon = location_champ.get('longitude')
        
        # Skip locations without valid coordinates
        if pd.isna(lat) or pd.isna(lon):
            continue
        
        location_stats.append({
            'location': location,
            'champion_count': champion_count,
            'observation_count': obs_count,
            'coverage_pct': coverage_pct,
            'avg_readiness': avg_readiness,
            'lat': lat,
            'lon': lon
        })
    
    location_df = pd.DataFrame(location_stats)
    
    if len(location_df) == 0:
        st.info("No champion locations are currently available to display.")
        return
    
    # Render the map
    render_location_map(location_df)
