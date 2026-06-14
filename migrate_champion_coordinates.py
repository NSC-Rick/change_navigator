"""
One-time migration utility to populate latitude/longitude for existing champions
"""

import sqlite3
from geocoding import geocode_location

DATABASE_NAME = "change_navigator.db"

def migrate_champion_coordinates(verbose=True):
    """
    Migrate existing champion records to populate latitude/longitude coordinates.
    
    For every champion where latitude or longitude is NULL:
    - Lookup location using geocode_location()
    - Populate latitude and longitude
    - Update database
    
    Args:
        verbose: If True, print detailed output. If False, suppress print statements.
    
    Returns:
        dict: Migration statistics
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get all champions with NULL coordinates
    cursor.execute("""
        SELECT id, champion_name, location, latitude, longitude
        FROM champions
        WHERE latitude IS NULL OR longitude IS NULL
    """)
    
    champions_to_migrate = cursor.fetchall()
    
    stats = {
        "total_champions": len(champions_to_migrate),
        "successfully_geocoded": 0,
        "failed_geocoding": 0,
        "skipped_empty_location": 0,
        "details": []
    }
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"CHAMPION COORDINATE MIGRATION")
        print(f"{'='*80}")
        print(f"Found {len(champions_to_migrate)} champions with missing coordinates\n")
    
    for champion in champions_to_migrate:
        champ_id, champ_name, location, current_lat, current_lon = champion
        
        # Skip if location is empty
        if not location or location.strip() == "":
            if verbose:
                print(f"⚠️  Champion '{champ_name}' (ID: {champ_id}) - No location specified, skipping")
            stats["skipped_empty_location"] += 1
            stats["details"].append({
                "id": champ_id,
                "name": champ_name,
                "location": location,
                "status": "skipped_empty_location"
            })
            continue
        
        # Geocode location
        coords = geocode_location(location)
        
        if coords["resolved"]:
            # Update champion with coordinates
            cursor.execute("""
                UPDATE champions
                SET latitude = ?, longitude = ?
                WHERE id = ?
            """, (coords["lat"], coords["lon"], champ_id))
            
            if verbose:
                print(f"✅ Champion '{champ_name}' (ID: {champ_id})")
                print(f"   Location: {location}")
                print(f"   Coordinates: {coords['lat']}, {coords['lon']}\n")
            
            stats["successfully_geocoded"] += 1
            stats["details"].append({
                "id": champ_id,
                "name": champ_name,
                "location": location,
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "status": "success"
            })
        else:
            if verbose:
                print(f"❌ Champion '{champ_name}' (ID: {champ_id})")
                print(f"   Location: '{location}' could not be geocoded")
                print(f"   This champion will not appear on the Location Insights map\n")
            
            stats["failed_geocoding"] += 1
            stats["details"].append({
                "id": champ_id,
                "name": champ_name,
                "location": location,
                "status": "failed_geocoding"
            })
    
    # Commit changes
    conn.commit()
    conn.close()
    
    # Print summary
    if verbose:
        print(f"{'='*80}")
        print(f"MIGRATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total champions processed: {stats['total_champions']}")
        print(f"✅ Successfully geocoded: {stats['successfully_geocoded']}")
        print(f"❌ Failed to geocode: {stats['failed_geocoding']}")
        print(f"⚠️  Skipped (empty location): {stats['skipped_empty_location']}")
        print(f"{'='*80}\n")
        
        if stats["failed_geocoding"] > 0:
            print("Champions with failed geocoding:")
            for detail in stats["details"]:
                if detail["status"] == "failed_geocoding":
                    print(f"  - {detail['name']}: '{detail['location']}'")
            print("\nSuggested actions:")
            print("  1. Edit champion location to use recognized format (e.g., 'Boston, MA')")
            print("  2. Or add location to geocoding.py lookup table")
            print("  3. Re-run migration after corrections\n")
    
    return stats

if __name__ == "__main__":
    print("Starting champion coordinate migration...")
    stats = migrate_champion_coordinates()
    
    if stats["successfully_geocoded"] > 0:
        print(f"✅ Migration complete! {stats['successfully_geocoded']} champions can now be displayed on the Location Insights map.")
    else:
        print("⚠️  No champions were successfully geocoded. Please check location formats.")
