"""
Repair corrupted observation records that have blob/binary project_id and champion_id values.

This script:
1. Identifies observations with blob-type IDs
2. Determines the intended integer values based on observation context
3. Updates records to use proper integer IDs
4. Verifies all observations are now retrievable
"""

import sqlite3
import pandas as pd

DATABASE_NAME = "change_navigator.db"

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_NAME)

def diagnose_corrupted_records():
    """Identify observations with blob/binary IDs"""
    conn = get_connection()
    
    print("=" * 80)
    print("DIAGNOSING CORRUPTED OBSERVATION RECORDS")
    print("=" * 80)
    
    # Get all observations
    query = """
        SELECT id, typeof(project_id) as project_id_type, typeof(champion_id) as champion_id_type,
               project_id, champion_id, observation_date, overall_status, readiness_score
        FROM observations
        ORDER BY id DESC
        LIMIT 15
    """
    
    df = pd.read_sql_query(query, conn)
    
    print("\nRecent Observations (showing type information):")
    print(df.to_string())
    
    # Identify corrupted records
    corrupted = df[(df['project_id_type'] != 'integer') | (df['champion_id_type'] != 'integer')]
    
    if len(corrupted) > 0:
        print(f"\n⚠️  Found {len(corrupted)} corrupted records:")
        print(corrupted[['id', 'project_id_type', 'champion_id_type', 'observation_date']].to_string())
    else:
        print("\n✅ No corrupted records found - all IDs are integers!")
    
    conn.close()
    return corrupted

def repair_corrupted_records():
    """Repair observations with blob IDs by converting to integers"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("REPAIRING CORRUPTED RECORDS")
    print("=" * 80)
    
    # Get corrupted records
    cursor.execute("""
        SELECT id, project_id, champion_id, observation_date
        FROM observations
        WHERE typeof(project_id) != 'integer' OR typeof(champion_id) != 'integer'
        ORDER BY id
    """)
    
    corrupted_records = cursor.fetchall()
    
    if not corrupted_records:
        print("\n✅ No corrupted records to repair!")
        conn.close()
        return
    
    print(f"\nFound {len(corrupted_records)} records to repair:")
    
    for record in corrupted_records:
        obs_id, project_id_raw, champion_id_raw, obs_date = record
        
        print(f"\nObservation ID {obs_id} (Date: {obs_date}):")
        print(f"  Current project_id: {project_id_raw} (type: {type(project_id_raw)})")
        print(f"  Current champion_id: {champion_id_raw} (type: {type(champion_id_raw)})")
        
        # Try to extract integer values from blob
        # Blob format appears to be little-endian 8-byte integer
        if isinstance(project_id_raw, bytes):
            # Convert bytes to integer (little-endian)
            project_id_int = int.from_bytes(project_id_raw, byteorder='little')
            print(f"  Extracted project_id: {project_id_int}")
        else:
            project_id_int = int(project_id_raw)
            print(f"  Converted project_id: {project_id_int}")
        
        if isinstance(champion_id_raw, bytes):
            champion_id_int = int.from_bytes(champion_id_raw, byteorder='little')
            print(f"  Extracted champion_id: {champion_id_int}")
        else:
            champion_id_int = int(champion_id_raw)
            print(f"  Converted champion_id: {champion_id_int}")
        
        # Update the record with proper integer values
        cursor.execute("""
            UPDATE observations
            SET project_id = ?, champion_id = ?
            WHERE id = ?
        """, (project_id_int, champion_id_int, obs_id))
        
        print(f"  ✅ Updated to project_id={project_id_int}, champion_id={champion_id_int}")
    
    conn.commit()
    print(f"\n✅ Repaired {len(corrupted_records)} records successfully!")
    conn.close()

def verify_repair():
    """Verify all observations now have integer IDs"""
    conn = get_connection()
    
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # Check for any remaining blob types
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM observations
        WHERE typeof(project_id) != 'integer' OR typeof(champion_id) != 'integer'
    """)
    
    remaining_corrupted = cursor.fetchone()[0]
    
    if remaining_corrupted > 0:
        print(f"\n⚠️  Still have {remaining_corrupted} corrupted records!")
    else:
        print("\n✅ All observations now have integer IDs!")
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM observations")
    total_obs = cursor.fetchone()[0]
    
    print(f"\nTotal observations in database: {total_obs}")
    
    # Show recent observations with proper types
    query = """
        SELECT id, project_id, champion_id, observation_date, overall_status, readiness_score,
               typeof(project_id) as pid_type, typeof(champion_id) as cid_type
        FROM observations
        ORDER BY id DESC
        LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    print("\nRecent observations (after repair):")
    print(df.to_string())
    
    conn.close()

def main():
    """Main repair process"""
    print("\n" + "=" * 80)
    print("OBSERVATION RECORD REPAIR UTILITY")
    print("=" * 80)
    
    # Step 1: Diagnose
    corrupted = diagnose_corrupted_records()
    
    if len(corrupted) == 0:
        print("\n✅ No repair needed - all records are clean!")
        return
    
    # Step 2: Repair
    repair_corrupted_records()
    
    # Step 3: Verify
    verify_repair()
    
    print("\n" + "=" * 80)
    print("REPAIR COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Refresh the application")
    print("2. Navigate to Initiative Workspace → Observations")
    print("3. Verify all 12 observations are now visible")
    print("4. Submit a new test observation to confirm fix is working")

if __name__ == "__main__":
    main()
