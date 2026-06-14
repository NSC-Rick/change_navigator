"""
Location Insights - Geographic visualization of champion participation and readiness
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database as db

# Mock coordinates for common locations (for MVP testing)
MOCK_COORDINATES = {
    # US Cities
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
    "Chicago": {"lat": 41.8781, "lon": -87.6298},
    "Houston": {"lat": 29.7604, "lon": -95.3698},
    "Phoenix": {"lat": 33.4484, "lon": -112.0740},
    "Philadelphia": {"lat": 39.9526, "lon": -75.1652},
    "San Antonio": {"lat": 29.4241, "lon": -98.4936},
    "San Diego": {"lat": 32.7157, "lon": -117.1611},
    "Dallas": {"lat": 32.7767, "lon": -96.7970},
    "San Jose": {"lat": 37.3382, "lon": -121.8863},
    "Austin": {"lat": 30.2672, "lon": -97.7431},
    "Seattle": {"lat": 47.6062, "lon": -122.3321},
    "Denver": {"lat": 39.7392, "lon": -104.9903},
    "Boston": {"lat": 42.3601, "lon": -71.0589},
    "Atlanta": {"lat": 33.7490, "lon": -84.3880},
    "Miami": {"lat": 25.7617, "lon": -80.1918},
    
    # International Cities
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
    "Toronto": {"lat": 43.6532, "lon": -79.3832},
    "Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Dubai": {"lat": 25.2048, "lon": 55.2708},
    "Berlin": {"lat": 52.5200, "lon": 13.4050},
    "Madrid": {"lat": 40.4168, "lon": -3.7038},
    "Rome": {"lat": 41.9028, "lon": 12.4964},
    "Amsterdam": {"lat": 52.3676, "lon": 4.9041},
    "Brussels": {"lat": 50.8503, "lon": 4.3517},
    "Zurich": {"lat": 47.3769, "lon": 8.5417},
    
    # Generic fallback
    "Unknown": {"lat": 0.0, "lon": 0.0}
}

def get_coordinates(location):
    """Get lat/lon coordinates for a location (mock data for MVP)"""
    if pd.isna(location) or location == "":
        return MOCK_COORDINATES["Unknown"]
    
    # Try exact match first
    if location in MOCK_COORDINATES:
        return MOCK_COORDINATES[location]
    
    # Try case-insensitive match
    for key in MOCK_COORDINATES:
        if key.lower() == location.lower():
            return MOCK_COORDINATES[key]
    
    # Default to Unknown
    return MOCK_COORDINATES["Unknown"]

def render_location_insights_tab(project_id, project):
    """Location Insights - Geographic visualization of champion participation and readiness"""
    
    st.markdown("### 🌍 Location Insights")
    st.caption("Geographic visualization of champion participation and readiness")
    
    # Get champions and observations data
    champions_df = db.get_champions_by_project(project_id)
    observations_df = db.get_observations_by_project(project_id)
    
    if len(champions_df) == 0:
        st.info("No champions assigned to this initiative yet.")
        return
    
    # Check if location data exists
    if 'location' not in champions_df.columns or champions_df['location'].isna().all():
        st.warning("⚠️ Location data is not available for champions. Please add location information in the Champions tab.")
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
        st.info("No location data available.")
        return
    
    # View toggle
    view_mode = st.radio(
        "View Mode",
        options=["📊 Table View", "🗺️ Map View"],
        horizontal=True,
        label_visibility="collapsed",
        key="location_insights_view_mode"
    )
    
    st.markdown("---")
    
    if view_mode == "📊 Table View":
        render_location_table(location_df)
    else:
        render_location_map(location_df)

def render_location_table(location_df):
    """Render location summary table"""
    
    st.markdown("#### Location Summary")
    
    # Format the dataframe for display
    display_df = location_df.copy()
    display_df['coverage_pct'] = display_df['coverage_pct'].apply(lambda x: f"{x:.1f}%")
    display_df['avg_readiness'] = display_df['avg_readiness'].apply(
        lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
    )
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'location': 'Location',
        'champion_count': 'Champions',
        'observation_count': 'Observations',
        'coverage_pct': 'Coverage %',
        'avg_readiness': 'Avg Readiness'
    })
    
    # Select columns to display
    display_df = display_df[['Location', 'Champions', 'Observations', 'Coverage %', 'Avg Readiness']]
    
    # Sort by readiness (convert back to numeric for sorting)
    display_df['_sort_readiness'] = location_df['avg_readiness']
    display_df = display_df.sort_values('_sort_readiness', ascending=False, na_position='last')
    display_df = display_df.drop('_sort_readiness', axis=1)
    
    # Display table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_locations = len(location_df)
        st.metric("📍 Total Locations", total_locations)
    
    with col2:
        avg_coverage = location_df['coverage_pct'].mean()
        st.metric("📊 Avg Coverage", f"{avg_coverage:.1f}%")
    
    with col3:
        overall_readiness = location_df['avg_readiness'].mean()
        if pd.notna(overall_readiness):
            st.metric("🎯 Overall Readiness", f"{overall_readiness:.1f}")
        else:
            st.metric("🎯 Overall Readiness", "N/A")

def render_location_map(location_df):
    """Render geographic map visualization"""
    
    # Filter out locations without valid coordinates
    map_df = location_df[
        (location_df['lat'] != 0) | (location_df['lon'] != 0)
    ].copy()
    
    if len(map_df) == 0:
        st.info("No champion locations are currently available to display.")
        return
    
    # Determine readiness color
    def get_readiness_color(readiness):
        if pd.isna(readiness):
            return "gray"
        elif readiness >= 8:
            return "green"
        elif readiness >= 6:
            return "yellow"
        else:
            return "red"
    
    map_df['color'] = map_df['avg_readiness'].apply(get_readiness_color)
    map_df['readiness_display'] = map_df['avg_readiness'].apply(
        lambda x: f"{x:.1f}" if pd.notna(x) else "N/A"
    )
    
    # Create hover text
    map_df['hover_text'] = map_df.apply(
        lambda row: f"<b>{row['location']}</b><br>" +
                    f"Champions: {row['champion_count']}<br>" +
                    f"Coverage: {row['coverage_pct']:.1f}%<br>" +
                    f"Avg Readiness: {row['readiness_display']}",
        axis=1
    )
    
    # Determine map scope (regional vs global)
    lat_range = map_df['lat'].max() - map_df['lat'].min()
    lon_range = map_df['lon'].max() - map_df['lon'].min()
    
    # If all locations are within a small region (e.g., USA), zoom in
    if lat_range < 50 and lon_range < 80:
        # Regional map
        center_lat = map_df['lat'].mean()
        center_lon = map_df['lon'].mean()
        
        # Determine if it's USA-focused
        if -130 < center_lon < -60 and 25 < center_lat < 50:
            scope = "usa"
        else:
            scope = "world"
    else:
        # Global map
        scope = "world"
    
    # Create the map
    fig = px.scatter_geo(
        map_df,
        lat='lat',
        lon='lon',
        hover_name='location'
    )
    
    # Set explicit height for better display
    fig.update_layout(height=600)
    
    # Render Plotly map
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend
    st.markdown("---")
    st.markdown("#### Readiness Legend")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("🟢 **Green**: Readiness ≥ 8")
    
    with col2:
        st.markdown("🟡 **Yellow**: Readiness 6-8")
    
    with col3:
        st.markdown("🔴 **Red**: Readiness < 6")
    
    with col4:
        st.markdown("⚪ **Gray**: No data")
    
    # Summary metrics below map
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        green_count = len(map_df[map_df['color'] == 'green'])
        st.metric("🟢 High Readiness Locations", green_count)
    
    with col2:
        yellow_count = len(map_df[map_df['color'] == 'yellow'])
        st.metric("🟡 Moderate Readiness Locations", yellow_count)
    
    with col3:
        red_count = len(map_df[map_df['color'] == 'red'])
        st.metric("🔴 Low Readiness Locations", red_count)
