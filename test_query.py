import sqlite3
import pandas as pd
import numpy as np

DATABASE_NAME = "change_navigator.db"

def test_project_id_types():
    """Test different project_id data types"""
    conn = sqlite3.connect(DATABASE_NAME)
    
    print("=" * 80)
    print("TESTING PROJECT_ID DATA TYPES")
    print("=" * 80)
    
    # Get projects
    projects_df = pd.read_sql_query("SELECT * FROM projects", conn)
    print("\nProjects DataFrame:")
    print(projects_df[['id', 'project_name']])
    print(f"\nDataFrame 'id' column dtype: {projects_df['id'].dtype}")
    
    # Test with first project
    first_project = projects_df.iloc[0]
    project_id = first_project['id']
    
    print(f"\nFirst project:")
    print(f"  Name: {first_project['project_name']}")
    print(f"  ID value: {project_id}")
    print(f"  ID type: {type(project_id)}")
    print(f"  ID dtype: {type(project_id).__name__}")
    
    # Test query with different types
    print("\n" + "=" * 80)
    print("TESTING QUERIES WITH DIFFERENT PROJECT_ID TYPES")
    print("=" * 80)
    
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
    
    print(f"\n1. Query with original value (type: {type(project_id).__name__})")
    result1 = pd.read_sql_query(query, conn, params=(project_id,))
    print(f"   Result count: {len(result1)}")
    
    print(f"\n2. Query with int() conversion")
    result2 = pd.read_sql_query(query, conn, params=(int(project_id),))
    print(f"   Result count: {len(result2)}")
    
    print(f"\n3. Query with str() conversion")
    result3 = pd.read_sql_query(query, conn, params=(str(project_id),))
    print(f"   Result count: {len(result3)}")
    
    # Check if it's a numpy type
    if isinstance(project_id, (np.integer, np.int64, np.int32)):
        print(f"\n4. Query with .item() conversion (numpy to python)")
        result4 = pd.read_sql_query(query, conn, params=(project_id.item(),))
        print(f"   Result count: {len(result4)}")
    
    # Test the exact pattern from app.py
    print("\n" + "=" * 80)
    print("SIMULATING APP.PY PATTERN")
    print("=" * 80)
    
    projects_df = pd.read_sql_query("""
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
    """, conn)
    
    print("\nPortfolio query result:")
    print(projects_df[['id', 'project_name', 'observation_count']])
    print(f"\nID column dtype: {projects_df['id'].dtype}")
    
    project_names = projects_df['project_name'].tolist()
    selected_project_name = project_names[0]
    
    print(f"\nSelected project name: {selected_project_name}")
    
    selected_project = projects_df[projects_df['project_name'] == selected_project_name].iloc[0]
    project_id = selected_project['id']
    
    print(f"Selected project_id: {project_id}")
    print(f"Type: {type(project_id)}")
    print(f"Type name: {type(project_id).__name__}")
    
    print(f"\nQuerying with this project_id...")
    result = pd.read_sql_query(query, conn, params=(project_id,))
    print(f"Result count: {len(result)}")
    
    if len(result) == 0:
        print("\n⚠️ FOUND THE BUG! Query returns 0 with this data type.")
        print("Testing conversions...")
        
        result_int = pd.read_sql_query(query, conn, params=(int(project_id),))
        print(f"  With int(): {len(result_int)} rows")
        
        if hasattr(project_id, 'item'):
            result_item = pd.read_sql_query(query, conn, params=(project_id.item(),))
            print(f"  With .item(): {len(result_item)} rows")
    
    conn.close()

if __name__ == "__main__":
    test_project_id_types()
