import database as db
import pandas as pd
from datetime import datetime, timedelta

def get_functional_heat_map():
    """Get readiness scores aggregated by department with trend analysis"""
    conn = db.get_connection()
    
    # Get current readiness by department
    query = """
        SELECT 
            c.department,
            COUNT(DISTINCT o.id) as observation_count,
            AVG(o.readiness_score) as avg_readiness,
            COUNT(DISTINCT c.id) as champion_count
        FROM observations o
        JOIN champions c ON o.champion_id = c.id
        GROUP BY c.department
        ORDER BY avg_readiness ASC
    """
    
    current_df = pd.read_sql_query(query, conn)
    
    # Get trend data (last 30 days vs previous 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    sixty_days_ago = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    
    trend_query = """
        SELECT 
            c.department,
            AVG(CASE 
                WHEN o.observation_date >= ? THEN o.readiness_score 
                ELSE NULL 
            END) as recent_readiness,
            AVG(CASE 
                WHEN o.observation_date >= ? AND o.observation_date < ? THEN o.readiness_score 
                ELSE NULL 
            END) as previous_readiness
        FROM observations o
        JOIN champions c ON o.champion_id = c.id
        GROUP BY c.department
    """
    
    trend_df = pd.read_sql_query(trend_query, conn, params=(thirty_days_ago, sixty_days_ago, thirty_days_ago))
    
    # Merge and calculate trend
    result_df = current_df.merge(trend_df, on='department', how='left')
    
    def calculate_trend(row):
        if pd.isna(row['recent_readiness']) or pd.isna(row['previous_readiness']):
            return 'Stable'
        diff = row['recent_readiness'] - row['previous_readiness']
        if diff > 0.5:
            return 'Up'
        elif diff < -0.5:
            return 'Down'
        else:
            return 'Stable'
    
    result_df['trend'] = result_df.apply(calculate_trend, axis=1)
    
    conn.close()
    return result_df

def get_geographic_heat_map():
    """Get readiness scores aggregated by location with trend analysis"""
    conn = db.get_connection()
    
    # Get current readiness by location
    query = """
        SELECT 
            c.location,
            COUNT(DISTINCT o.id) as observation_count,
            AVG(o.readiness_score) as avg_readiness,
            COUNT(DISTINCT c.id) as champion_count
        FROM observations o
        JOIN champions c ON o.champion_id = c.id
        WHERE c.location IS NOT NULL AND c.location != 'Unknown'
        GROUP BY c.location
        ORDER BY avg_readiness ASC
    """
    
    current_df = pd.read_sql_query(query, conn)
    
    # Get trend data
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    sixty_days_ago = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    
    trend_query = """
        SELECT 
            c.location,
            AVG(CASE 
                WHEN o.observation_date >= ? THEN o.readiness_score 
                ELSE NULL 
            END) as recent_readiness,
            AVG(CASE 
                WHEN o.observation_date >= ? AND o.observation_date < ? THEN o.readiness_score 
                ELSE NULL 
            END) as previous_readiness
        FROM observations o
        JOIN champions c ON o.champion_id = c.id
        WHERE c.location IS NOT NULL AND c.location != 'Unknown'
        GROUP BY c.location
    """
    
    trend_df = pd.read_sql_query(trend_query, conn, params=(thirty_days_ago, sixty_days_ago, thirty_days_ago))
    
    # Merge and calculate trend
    result_df = current_df.merge(trend_df, on='location', how='left')
    
    def calculate_trend(row):
        if pd.isna(row['recent_readiness']) or pd.isna(row['previous_readiness']):
            return 'Stable'
        diff = row['recent_readiness'] - row['previous_readiness']
        if diff > 0.5:
            return 'Up'
        elif diff < -0.5:
            return 'Down'
        else:
            return 'Stable'
    
    result_df['trend'] = result_df.apply(calculate_trend, axis=1)
    
    conn.close()
    return result_df

def get_function_location_matrix():
    """Get readiness matrix by department and location"""
    conn = db.get_connection()
    
    query = """
        SELECT 
            c.department,
            c.location,
            AVG(o.readiness_score) as avg_readiness,
            COUNT(o.id) as observation_count
        FROM observations o
        JOIN champions c ON o.champion_id = c.id
        WHERE c.location IS NOT NULL AND c.location != 'Unknown'
        GROUP BY c.department, c.location
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Pivot to create matrix
    if len(df) > 0:
        matrix = df.pivot_table(
            index='department', 
            columns='location', 
            values='avg_readiness',
            aggfunc='mean'
        )
        return matrix
    else:
        return pd.DataFrame()

def get_change_saturation():
    """Calculate active project impact by functional area"""
    conn = db.get_connection()
    
    query = """
        SELECT 
            c.department,
            COUNT(DISTINCT c.project_id) as active_projects,
            COUNT(DISTINCT c.id) as champions_assigned,
            COUNT(DISTINCT o.id) as total_observations,
            AVG(o.readiness_score) as avg_readiness
        FROM champions c
        LEFT JOIN observations o ON c.id = o.champion_id
        JOIN projects p ON c.project_id = p.id
        WHERE p.status IN ('Active', 'Go-Live', 'Planning')
        GROUP BY c.department
        ORDER BY active_projects DESC, avg_readiness ASC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_observation_coverage(days: int = 7):
    """Get observation coverage metrics for the last N days"""
    conn = db.get_connection()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Overall coverage
    overall_query = """
        SELECT 
            COUNT(DISTINCT c.id) as total_champions,
            COUNT(DISTINCT CASE 
                WHEN o.observation_date >= ? THEN c.id 
                ELSE NULL 
            END) as active_champions,
            COUNT(CASE 
                WHEN o.observation_date >= ? THEN o.id 
                ELSE NULL 
            END) as recent_observations
        FROM champions c
        LEFT JOIN observations o ON c.id = o.champion_id
    """
    
    overall_df = pd.read_sql_query(overall_query, conn, params=(cutoff_date, cutoff_date))
    
    # By project
    project_query = """
        SELECT 
            p.project_name,
            COUNT(DISTINCT c.id) as total_champions,
            COUNT(DISTINCT CASE 
                WHEN o.observation_date >= ? THEN c.id 
                ELSE NULL 
            END) as active_champions,
            COUNT(CASE 
                WHEN o.observation_date >= ? THEN o.id 
                ELSE NULL 
            END) as recent_observations
        FROM projects p
        LEFT JOIN champions c ON p.id = c.project_id
        LEFT JOIN observations o ON c.id = o.champion_id
        GROUP BY p.id, p.project_name
        ORDER BY p.project_name
    """
    
    project_df = pd.read_sql_query(project_query, conn, params=(cutoff_date, cutoff_date))
    
    # By department
    dept_query = """
        SELECT 
            c.department,
            COUNT(DISTINCT c.id) as total_champions,
            COUNT(DISTINCT CASE 
                WHEN o.observation_date >= ? THEN c.id 
                ELSE NULL 
            END) as active_champions,
            COUNT(CASE 
                WHEN o.observation_date >= ? THEN o.id 
                ELSE NULL 
            END) as recent_observations
        FROM champions c
        LEFT JOIN observations o ON c.id = o.champion_id
        GROUP BY c.department
        ORDER BY c.department
    """
    
    dept_df = pd.read_sql_query(dept_query, conn, params=(cutoff_date, cutoff_date))
    
    # By location
    location_query = """
        SELECT 
            c.location,
            COUNT(DISTINCT c.id) as total_champions,
            COUNT(DISTINCT CASE 
                WHEN o.observation_date >= ? THEN c.id 
                ELSE NULL 
            END) as active_champions,
            COUNT(CASE 
                WHEN o.observation_date >= ? THEN o.id 
                ELSE NULL 
            END) as recent_observations
        FROM champions c
        LEFT JOIN observations o ON c.id = o.champion_id
        WHERE c.location IS NOT NULL AND c.location != 'Unknown'
        GROUP BY c.location
        ORDER BY c.location
    """
    
    location_df = pd.read_sql_query(location_query, conn, params=(cutoff_date, cutoff_date))
    
    conn.close()
    
    # Calculate coverage percentages
    for df in [overall_df, project_df, dept_df, location_df]:
        if len(df) > 0:
            df['coverage_pct'] = (df['active_champions'] / df['total_champions'] * 100).fillna(0)
    
    return {
        'overall': overall_df,
        'by_project': project_df,
        'by_department': dept_df,
        'by_location': location_df
    }

def get_readiness_thresholds():
    """Return configurable readiness thresholds for color coding"""
    return {
        'green': 8.0,
        'yellow': 6.0,
        'red': 0.0
    }

def get_readiness_color_category(score):
    """Get color category for a readiness score"""
    if pd.isna(score):
        return 'gray'
    
    thresholds = get_readiness_thresholds()
    
    if score >= thresholds['green']:
        return 'green'
    elif score >= thresholds['yellow']:
        return 'yellow'
    else:
        return 'red'
