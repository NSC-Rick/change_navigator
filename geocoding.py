"""
Geocoding utilities for automatic location coordinate resolution
"""

# Built-in location lookup table for MVP
# Format: "Location Name": {"lat": latitude, "lon": longitude}
LOCATION_LOOKUP = {
    # United States - Major Cities
    "Boston, MA": {"lat": 42.3601, "lon": -71.0589},
    "New York, NY": {"lat": 40.7128, "lon": -74.0060},
    "Chicago, IL": {"lat": 41.8781, "lon": -87.6298},
    "Dallas, TX": {"lat": 32.7767, "lon": -96.7970},
    "Houston, TX": {"lat": 29.7604, "lon": -95.3698},
    "Los Angeles, CA": {"lat": 34.0522, "lon": -118.2437},
    "San Francisco, CA": {"lat": 37.7749, "lon": -122.4194},
    "Seattle, WA": {"lat": 47.6062, "lon": -122.3321},
    "Denver, CO": {"lat": 39.7392, "lon": -104.9903},
    "Atlanta, GA": {"lat": 33.7490, "lon": -84.3880},
    "Miami, FL": {"lat": 25.7617, "lon": -80.1918},
    "Phoenix, AZ": {"lat": 33.4484, "lon": -112.0740},
    "Philadelphia, PA": {"lat": 39.9526, "lon": -75.1652},
    "San Diego, CA": {"lat": 32.7157, "lon": -117.1611},
    "Austin, TX": {"lat": 30.2672, "lon": -97.7431},
    "Burlington, VT": {"lat": 44.4759, "lon": -73.2121},
    
    # Canada - Major Cities
    "Toronto, ON": {"lat": 43.6532, "lon": -79.3832},
    "Montreal, QC": {"lat": 45.5017, "lon": -73.5673},
    "Vancouver, BC": {"lat": 49.2827, "lon": -123.1207},
    "Calgary, AB": {"lat": 51.0447, "lon": -114.0719},
    "Ottawa, ON": {"lat": 45.4215, "lon": -75.6972},
    
    # United Kingdom
    "London, UK": {"lat": 51.5074, "lon": -0.1278},
    "Manchester, UK": {"lat": 53.4808, "lon": -2.2426},
    "Birmingham, UK": {"lat": 52.4862, "lon": -1.8904},
    "Edinburgh, UK": {"lat": 55.9533, "lon": -3.1883},
    
    # Europe
    "Paris, France": {"lat": 48.8566, "lon": 2.3522},
    "Berlin, Germany": {"lat": 52.5200, "lon": 13.4050},
    "Madrid, Spain": {"lat": 40.4168, "lon": -3.7038},
    "Rome, Italy": {"lat": 41.9028, "lon": 12.4964},
    "Amsterdam, Netherlands": {"lat": 52.3676, "lon": 4.9041},
    "Brussels, Belgium": {"lat": 50.8503, "lon": 4.3517},
    "Zurich, Switzerland": {"lat": 47.3769, "lon": 8.5417},
    
    # Asia Pacific
    "Tokyo, Japan": {"lat": 35.6762, "lon": 139.6503},
    "Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
    "Sydney, Australia": {"lat": -33.8688, "lon": 151.2093},
    "Melbourne, Australia": {"lat": -37.8136, "lon": 144.9631},
    "Mumbai, India": {"lat": 19.0760, "lon": 72.8777},
    "Shanghai, China": {"lat": 31.2304, "lon": 121.4737},
    "Seoul, South Korea": {"lat": 37.5665, "lon": 126.9780},
    
    # Middle East
    "Dubai, UAE": {"lat": 25.2048, "lon": 55.2708},
    "Tel Aviv, Israel": {"lat": 32.0853, "lon": 34.7818},
    
    # Latin America
    "Mexico City, Mexico": {"lat": 19.4326, "lon": -99.1332},
    "São Paulo, Brazil": {"lat": -23.5505, "lon": -46.6333},
    "Buenos Aires, Argentina": {"lat": -34.6037, "lon": -58.3816},
    
    # Simplified versions (without state/country)
    "Boston": {"lat": 42.3601, "lon": -71.0589},
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Chicago": {"lat": 41.8781, "lon": -87.6298},
    "Dallas": {"lat": 32.7767, "lon": -96.7970},
    "Houston": {"lat": 29.7604, "lon": -95.3698},
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
    "San Francisco": {"lat": 37.7749, "lon": -122.4194},
    "Seattle": {"lat": 47.6062, "lon": -122.3321},
    "Denver": {"lat": 39.7392, "lon": -104.9903},
    "Atlanta": {"lat": 33.7490, "lon": -84.3880},
    "Miami": {"lat": 25.7617, "lon": -80.1918},
    "Phoenix": {"lat": 33.4484, "lon": -112.0740},
    "Philadelphia": {"lat": 39.9526, "lon": -75.1652},
    "Toronto": {"lat": 43.6532, "lon": -79.3832},
    "Montreal": {"lat": 45.5017, "lon": -73.5673},
    "Vancouver": {"lat": 49.2827, "lon": -123.1207},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
}

def geocode_location(location_text):
    """
    Resolve location text to geographic coordinates.
    
    Args:
        location_text: Location string (e.g., "Boston, MA", "Boston MA", "Toronto, ON")
    
    Returns:
        dict: {"lat": latitude, "lon": longitude, "resolved": True/False}
              Returns None values if location cannot be resolved
    """
    if not location_text or location_text.strip() == "":
        return {"lat": None, "lon": None, "resolved": False}
    
    # Normalize location text
    location_normalized = location_text.strip()
    
    # Try exact match first
    if location_normalized in LOCATION_LOOKUP:
        coords = LOCATION_LOOKUP[location_normalized]
        return {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "resolved": True
        }
    
    # Try case-insensitive match
    for key, coords in LOCATION_LOOKUP.items():
        if key.lower() == location_normalized.lower():
            return {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "resolved": True
            }
    
    # Try with comma added (e.g., "Boston MA" -> "Boston, MA")
    # This handles cases where user enters location without comma
    if "," not in location_normalized:
        # Try adding comma before last word
        parts = location_normalized.rsplit(None, 1)  # Split on last whitespace
        if len(parts) == 2:
            location_with_comma = f"{parts[0]}, {parts[1]}"
            
            # Try exact match with comma
            if location_with_comma in LOCATION_LOOKUP:
                coords = LOCATION_LOOKUP[location_with_comma]
                return {
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "resolved": True
                }
            
            # Try case-insensitive match with comma
            for key, coords in LOCATION_LOOKUP.items():
                if key.lower() == location_with_comma.lower():
                    return {
                        "lat": coords["lat"],
                        "lon": coords["lon"],
                        "resolved": True
                    }
    
    # Location not found in lookup table
    return {"lat": None, "lon": None, "resolved": False}

def get_all_known_locations():
    """
    Get list of all locations in the lookup table.
    Useful for autocomplete or validation.
    
    Returns:
        list: Sorted list of location names
    """
    return sorted(LOCATION_LOOKUP.keys())

def is_location_known(location_text):
    """
    Check if a location can be geocoded.
    
    Args:
        location_text: Location string to check
    
    Returns:
        bool: True if location is in lookup table
    """
    result = geocode_location(location_text)
    return result["resolved"]
