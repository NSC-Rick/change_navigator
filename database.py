import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from geocoding import geocode_location

DATABASE_NAME = "change_navigator.db"

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with all required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            client_name TEXT,
            project_description TEXT,
            sponsor_name TEXT NOT NULL,
            project_manager TEXT,
            change_lead TEXT,
            start_date TEXT NOT NULL,
            go_live_date TEXT,
            end_date TEXT,
            status TEXT NOT NULL,
            business_unit TEXT
        )
    """)
    
    migrate_database(cursor)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS champions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            champion_name TEXT NOT NULL,
            department TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            business_unit TEXT,
            manager TEXT,
            region TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            champion_id INTEGER NOT NULL,
            observation_date TEXT NOT NULL,
            overall_status TEXT NOT NULL,
            readiness_score INTEGER NOT NULL,
            what_are_you_hearing TEXT,
            questions_emerging TEXT,
            leadership_should_know TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (champion_id) REFERENCES champions (id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            summary_date TEXT NOT NULL,
            summary_text TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    
    conn.commit()
    conn.close()

def migrate_database(cursor):
    """Migrate existing database to add new columns if they don't exist"""
    # Migrate projects table
    cursor.execute("PRAGMA table_info(projects)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'client_name' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN client_name TEXT")
    
    if 'project_description' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN project_description TEXT")
    
    if 'project_manager' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN project_manager TEXT")
    
    if 'change_lead' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN change_lead TEXT")
    
    if 'go_live_date' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN go_live_date TEXT")
    
    if 'business_unit' not in columns:
        cursor.execute("ALTER TABLE projects ADD COLUMN business_unit TEXT")
    
    # Migrate champions table
    cursor.execute("PRAGMA table_info(champions)")
    champ_columns = [column[1] for column in cursor.fetchall()]
    
    if 'location' not in champ_columns:
        cursor.execute("ALTER TABLE champions ADD COLUMN location TEXT DEFAULT 'Unknown'")
    
    if 'business_unit' not in champ_columns:
        cursor.execute("ALTER TABLE champions ADD COLUMN business_unit TEXT")
    
    if 'manager' not in champ_columns:
        cursor.execute("ALTER TABLE champions ADD COLUMN manager TEXT")
    
    if 'region' not in champ_columns:
        cursor.execute("ALTER TABLE champions ADD COLUMN region TEXT")
    
    if 'latitude' not in champ_columns:
        cursor.execute("ALTER TABLE champions ADD COLUMN latitude REAL")
    
    if 'longitude' not in champ_columns:
        cursor.execute("ALTER TABLE champions ADD COLUMN longitude REAL")

def clear_all_data():
    """Clear all data from database and reset auto-increment counters"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM ai_summaries")
    cursor.execute("DELETE FROM observations")
    cursor.execute("DELETE FROM champions")
    cursor.execute("DELETE FROM projects")
    
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='ai_summaries'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='observations'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='champions'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='projects'")
    
    conn.commit()
    conn.close()

def diagnose_data_integrity():
    """Diagnose data integrity issues"""
    conn = get_connection()
    
    issues = []
    
    orphaned_obs = pd.read_sql_query("""
        SELECT o.id, o.project_id, o.champion_id
        FROM observations o
        LEFT JOIN champions c ON o.champion_id = c.id
        WHERE c.id IS NULL
    """, conn)
    
    if len(orphaned_obs) > 0:
        issues.append(f"Found {len(orphaned_obs)} orphaned observations (champion_id doesn't exist)")
    
    orphaned_champs = pd.read_sql_query("""
        SELECT c.id, c.project_id, c.champion_name
        FROM champions c
        LEFT JOIN projects p ON c.project_id = p.id
        WHERE p.id IS NULL
    """, conn)
    
    if len(orphaned_champs) > 0:
        issues.append(f"Found {len(orphaned_champs)} orphaned champions (project_id doesn't exist)")
    
    conn.close()
    
    return issues

def get_all_projects(include_archived: bool = False) -> pd.DataFrame:
    """Get all projects with stats. By default, excludes archived projects."""
    conn = get_connection()
    
    where_clause = "" if include_archived else "WHERE p.status != 'Archived'"
    
    query = f"""
        SELECT 
            p.id,
            p.project_name,
            p.client_name,
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
        {where_clause}
        GROUP BY p.id, p.project_name, p.client_name, p.sponsor_name, p.status, p.start_date, p.end_date
        ORDER BY p.project_name
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_project_by_id(project_id: int) -> Optional[Dict[str, Any]]:
    """Get project by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    project_id = int(project_id)
    
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_champions_by_project(project_id: int) -> pd.DataFrame:
    """Get all champions for a project"""
    conn = get_connection()
    
    project_id = int(project_id)
    
    query = """
        SELECT 
            c.*,
            COUNT(o.id) as observation_count
        FROM champions c
        LEFT JOIN observations o ON c.id = o.champion_id
        WHERE c.project_id = ?
        GROUP BY c.id
        ORDER BY c.champion_name
    """
    
    df = pd.read_sql_query(query, conn, params=(project_id,))
    conn.close()
    return df

def get_observations_by_project(project_id: int) -> pd.DataFrame:
    """Get all observations for a project"""
    conn = get_connection()
    
    project_id = int(project_id)
    
    query = """
        SELECT 
            o.*,
            c.champion_name,
            c.department
        FROM observations o
        JOIN champions c ON o.champion_id = c.id
        WHERE o.project_id = ?
        ORDER BY o.observation_date DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(project_id,))
    conn.close()
    return df

def add_project(project_name: str, sponsor_name: str, start_date: str, end_date: str, status: str,
                client_name: str = None, project_description: str = None, project_manager: str = None, 
                change_lead: str = None, go_live_date: str = None, business_unit: str = None) -> int:
    """Add a new project"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO projects (project_name, client_name, project_description, sponsor_name, project_manager, 
                             change_lead, start_date, go_live_date, end_date, status, business_unit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_name, client_name, project_description, sponsor_name, project_manager, 
          change_lead, start_date, go_live_date, end_date, status, business_unit))
    
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def update_project(project_id: int, project_name: str, sponsor_name: str, 
                   start_date: str, end_date: str, status: str,
                   client_name: str = None, project_description: str = None, project_manager: str = None,
                   change_lead: str = None, go_live_date: str = None, business_unit: str = None) -> bool:
    """Update an existing project"""
    conn = get_connection()
    cursor = conn.cursor()
    
    project_id = int(project_id)
    
    cursor.execute("""
        UPDATE projects 
        SET project_name = ?,
            client_name = ?,
            project_description = ?,
            sponsor_name = ?,
            project_manager = ?,
            change_lead = ?,
            start_date = ?,
            go_live_date = ?,
            end_date = ?,
            status = ?,
            business_unit = ?
        WHERE id = ?
    """, (project_name, client_name, project_description, sponsor_name, project_manager,
          change_lead, start_date, go_live_date, end_date, status, business_unit, project_id))
    
    conn.commit()
    conn.close()
    return True

def add_champion(project_id: int, champion_name: str, department: str, location: str, 
                 email: str, role: str, business_unit: str = None, 
                 manager: str = None, region: str = None) -> int:
    """Add a new champion with automatic geocoding"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Automatically geocode location
    coords = geocode_location(location)
    latitude = coords["lat"]
    longitude = coords["lon"]
    
    cursor.execute("""
        INSERT INTO champions (project_id, champion_name, department, location, latitude, longitude,
                              email, role, business_unit, manager, region)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, champion_name, department, location, latitude, longitude,
          email, role, business_unit, manager, region))
    
    champion_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return champion_id

def update_champion(champion_id: int, champion_name: str, department: str, location: str,
                   email: str, role: str, business_unit: str = None,
                   manager: str = None, region: str = None) -> bool:
    """Update an existing champion with automatic geocoding"""
    conn = get_connection()
    cursor = conn.cursor()
    
    champion_id = int(champion_id)
    
    # Automatically geocode location
    coords = geocode_location(location)
    latitude = coords["lat"]
    longitude = coords["lon"]
    
    cursor.execute("""
        UPDATE champions
        SET champion_name = ?,
            department = ?,
            location = ?,
            latitude = ?,
            longitude = ?,
            email = ?,
            role = ?,
            business_unit = ?,
            manager = ?,
            region = ?
        WHERE id = ?
    """, (champion_name, department, location, latitude, longitude, email, role,
          business_unit, manager, region, champion_id))
    
    conn.commit()
    conn.close()
    return True

def delete_champion(champion_id: int) -> bool:
    """Delete a champion (only if they have no observations)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    champion_id = int(champion_id)
    
    # Check if champion has observations
    cursor.execute("SELECT COUNT(*) FROM observations WHERE champion_id = ?", (champion_id,))
    obs_count = cursor.fetchone()[0]
    
    if obs_count > 0:
        conn.close()
        return False
    
    cursor.execute("DELETE FROM champions WHERE id = ?", (champion_id,))
    
    conn.commit()
    conn.close()
    return True

def add_observation(project_id: int, champion_id: int, overall_status: str, 
                   readiness_score: int, what_are_you_hearing: str, 
                   questions_emerging: str, leadership_should_know: str) -> int:
    """Add a new observation"""
    print(f"🔍 DEBUG: add_observation() called")
    print(f"  Database: {DATABASE_NAME}")
    print(f"  Project ID: {project_id}, Champion ID: {champion_id}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ensure IDs are native Python integers, not numpy/pandas types
    project_id = int(project_id)
    champion_id = int(champion_id)
    readiness_score = int(readiness_score)
    
    observation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"  Executing INSERT...")
    cursor.execute("""
        INSERT INTO observations (project_id, champion_id, observation_date, overall_status, 
                                 readiness_score, what_are_you_hearing, questions_emerging, 
                                 leadership_should_know)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (project_id, champion_id, observation_date, overall_status, readiness_score, 
          what_are_you_hearing, questions_emerging, leadership_should_know))
    
    observation_id = cursor.lastrowid
    print(f"  INSERT complete. Observation ID: {observation_id}")
    
    print(f"  Executing COMMIT...")
    conn.commit()
    print(f"  COMMIT complete.")
    
    # Verify the record exists
    cursor.execute("SELECT COUNT(*) FROM observations WHERE id = ?", (observation_id,))
    count = cursor.fetchone()[0]
    print(f"  Verification: Record exists = {count == 1}")
    
    conn.close()
    print(f"  Connection closed. Returning observation_id: {observation_id}")
    return observation_id

def add_ai_summary(project_id: int, summary_text: str) -> int:
    """Add a new AI summary"""
    conn = get_connection()
    cursor = conn.cursor()
    
    summary_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO ai_summaries (project_id, summary_date, summary_text)
        VALUES (?, ?, ?)
    """, (project_id, summary_date, summary_text))
    
    summary_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return summary_id

def get_latest_summary(project_id: int) -> Optional[Dict[str, Any]]:
    """Get the latest AI summary for a project"""
    conn = get_connection()
    cursor = conn.cursor()
    
    project_id = int(project_id)
    
    cursor.execute("""
        SELECT * FROM ai_summaries 
        WHERE project_id = ? 
        ORDER BY summary_date DESC 
        LIMIT 1
    """, (project_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_project_stats(project_id: int) -> Dict[str, Any]:
    """Get comprehensive stats for a project"""
    conn = get_connection()
    
    project_id = int(project_id)
    
    query = """
        SELECT 
            COUNT(DISTINCT c.id) as champion_count,
            COUNT(DISTINCT o.id) as observation_count,
            ROUND(AVG(o.readiness_score), 1) as avg_readiness_score,
            MAX(o.observation_date) as latest_observation_date
        FROM projects p
        LEFT JOIN champions c ON p.id = c.project_id
        LEFT JOIN observations o ON p.id = o.project_id
        WHERE p.id = ?
    """
    
    df = pd.read_sql_query(query, conn, params=(project_id,))
    conn.close()
    
    if len(df) > 0:
        return df.iloc[0].to_dict()
    return {}

def get_readiness_trend(project_id: int) -> pd.DataFrame:
    """Get readiness score trend over time"""
    conn = get_connection()
    
    project_id = int(project_id)
    
    query = """
        SELECT 
            DATE(observation_date) as date,
            ROUND(AVG(readiness_score), 1) as avg_readiness
        FROM observations
        WHERE project_id = ?
        GROUP BY DATE(observation_date)
        ORDER BY date
    """
    
    df = pd.read_sql_query(query, conn, params=(project_id,))
    conn.close()
    return df

def get_observations_by_department(project_id: int) -> pd.DataFrame:
    """Get observation count by department"""
    conn = get_connection()
    
    project_id = int(project_id)
    
    query = """
        SELECT 
            c.department,
            COUNT(o.id) as observation_count,
            ROUND(AVG(o.readiness_score), 1) as avg_readiness
        FROM observations o
        JOIN champions c ON o.champion_id = c.id
        WHERE o.project_id = ?
        GROUP BY c.department
        ORDER BY observation_count DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(project_id,))
    conn.close()
    return df

def archive_project(project_id: int) -> bool:
    """Archive a project by setting its status to 'Archived'"""
    conn = get_connection()
    cursor = conn.cursor()
    
    project_id = int(project_id)
    
    cursor.execute("""
        UPDATE projects 
        SET status = 'Archived'
        WHERE id = ?
    """, (project_id,))
    
    conn.commit()
    conn.close()
    return True

def delete_project(project_id: int) -> bool:
    """Hard delete a project and all associated data (champions, observations, summaries)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    project_id = int(project_id)
    
    # Delete in order: observations, summaries, champions, then project
    cursor.execute("DELETE FROM observations WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM ai_summaries WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM champions WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    
    conn.commit()
    conn.close()
    return True
