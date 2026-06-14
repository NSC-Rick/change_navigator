import sqlite3
import pandas as pd

DATABASE_NAME = "change_navigator.db"

def audit_database():
    """Perform comprehensive database audit"""
    conn = sqlite3.connect(DATABASE_NAME)
    
    print("=" * 80)
    print("DATABASE AUDIT - CHANGE NAVIGATOR")
    print("=" * 80)
    
    print("\n1. PROJECTS TABLE")
    print("-" * 80)
    projects = pd.read_sql_query("SELECT * FROM projects", conn)
    print(f"Total projects: {len(projects)}")
    print(projects[['id', 'project_name', 'status']])
    
    print("\n2. CHAMPIONS TABLE")
    print("-" * 80)
    champions = pd.read_sql_query("SELECT * FROM champions", conn)
    print(f"Total champions: {len(champions)}")
    print(champions[['id', 'project_id', 'champion_name', 'department']])
    
    print("\n3. OBSERVATIONS TABLE")
    print("-" * 80)
    observations = pd.read_sql_query("SELECT * FROM observations", conn)
    print(f"Total observations: {len(observations)}")
    if len(observations) > 0:
        print(observations[['id', 'project_id', 'champion_id', 'observation_date', 'overall_status']])
    
    print("\n4. FOREIGN KEY VERIFICATION")
    print("-" * 80)
    
    print("\n4a. Observations.project_id -> Projects.id")
    orphaned_project = pd.read_sql_query("""
        SELECT o.id as obs_id, o.project_id, p.id as project_exists
        FROM observations o
        LEFT JOIN projects p ON o.project_id = p.id
        WHERE p.id IS NULL
    """, conn)
    print(f"Orphaned observations (invalid project_id): {len(orphaned_project)}")
    if len(orphaned_project) > 0:
        print(orphaned_project)
    
    print("\n4b. Observations.champion_id -> Champions.id")
    orphaned_champion = pd.read_sql_query("""
        SELECT o.id as obs_id, o.champion_id, c.id as champion_exists
        FROM observations o
        LEFT JOIN champions c ON o.champion_id = c.id
        WHERE c.id IS NULL
    """, conn)
    print(f"Orphaned observations (invalid champion_id): {len(orphaned_champion)}")
    if len(orphaned_champion) > 0:
        print(orphaned_champion)
    
    print("\n4c. Champions.project_id -> Projects.id")
    orphaned_champ_project = pd.read_sql_query("""
        SELECT c.id as champ_id, c.project_id, p.id as project_exists
        FROM champions c
        LEFT JOIN projects p ON c.project_id = p.id
        WHERE p.id IS NULL
    """, conn)
    print(f"Orphaned champions (invalid project_id): {len(orphaned_champ_project)}")
    if len(orphaned_champ_project) > 0:
        print(orphaned_champ_project)
    
    print("\n5. OBSERVATION COUNTS BY PROJECT")
    print("-" * 80)
    obs_by_project = pd.read_sql_query("""
        SELECT project_id, COUNT(*) as count
        FROM observations
        GROUP BY project_id
        ORDER BY project_id
    """, conn)
    print("Direct count from observations table:")
    print(obs_by_project)
    
    print("\n6. PORTFOLIO VIEW QUERY (get_all_projects)")
    print("-" * 80)
    portfolio_query = """
        SELECT 
            p.id,
            p.project_name,
            p.sponsor_name,
            p.status,
            p.start_date,
            p.end_date,
            COUNT(DISTINCT c.id) as champion_count,
            COUNT(DISTINCT o.id) as observation_count,
            ROUND(AVG(o.readiness_score), 1) as avg_readiness_score
        FROM projects p
        LEFT JOIN champions c ON p.id = c.project_id
        LEFT JOIN observations o ON p.id = o.project_id
        GROUP BY p.id, p.project_name, p.sponsor_name, p.status, p.start_date, p.end_date
        ORDER BY p.project_name
    """
    portfolio_result = pd.read_sql_query(portfolio_query, conn)
    print("Portfolio View query result:")
    print(portfolio_result[['id', 'project_name', 'champion_count', 'observation_count', 'avg_readiness_score']])
    
    print("\n7. AI SUMMARY QUERY (get_observations_by_project)")
    print("-" * 80)
    for project_id in projects['id'].tolist():
        ai_query = """
            SELECT 
                o.*,
                c.champion_name,
                c.department
            FROM observations o
            JOIN champions c ON o.champion_id = c.id
            WHERE o.project_id = ?
            ORDER BY o.observation_date DESC
        """
        ai_result = pd.read_sql_query(ai_query, conn, params=(project_id,))
        print(f"Project ID {project_id}: {len(ai_result)} observations (JOIN query)")
    
    print("\n8. DETAILED ANALYSIS FOR EACH PROJECT")
    print("-" * 80)
    for project_id in projects['id'].tolist():
        project_name = projects[projects['id'] == project_id]['project_name'].values[0]
        print(f"\nProject ID {project_id}: {project_name}")
        
        raw_obs = pd.read_sql_query("SELECT * FROM observations WHERE project_id = ?", conn, params=(project_id,))
        print(f"  Raw observations: {len(raw_obs)}")
        
        project_champs = pd.read_sql_query("SELECT * FROM champions WHERE project_id = ?", conn, params=(project_id,))
        print(f"  Champions: {len(project_champs)}")
        
        if len(raw_obs) > 0 and len(project_champs) > 0:
            print(f"  Champion IDs in champions table: {sorted(project_champs['id'].tolist())}")
            print(f"  Champion IDs referenced in observations: {sorted(raw_obs['champion_id'].unique().tolist())}")
            
            obs_champ_ids = set(raw_obs['champion_id'].unique())
            actual_champ_ids = set(project_champs['id'].tolist())
            
            missing = obs_champ_ids - actual_champ_ids
            if missing:
                print(f"  ⚠️ MISMATCH: Observations reference champion IDs {missing} which don't exist!")
    
    print("\n9. SQLITE_SEQUENCE (AUTO-INCREMENT TRACKING)")
    print("-" * 80)
    try:
        sequence = pd.read_sql_query("SELECT * FROM sqlite_sequence", conn)
        print(sequence)
    except:
        print("No sqlite_sequence table (no auto-increment used yet)")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    audit_database()
