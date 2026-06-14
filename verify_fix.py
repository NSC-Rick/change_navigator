import database as db
import pandas as pd

print("=" * 80)
print("VERIFYING FIX FOR NUMPY.INT64 BUG")
print("=" * 80)

# Get projects using the same pattern as app.py
projects_df = db.get_all_projects()

print("\nProjects from get_all_projects():")
print(projects_df[['id', 'project_name', 'observation_count']])
print(f"\nID column dtype: {projects_df['id'].dtype}")

# Simulate app.py pattern
project_names = projects_df['project_name'].tolist()
selected_project_name = project_names[0]

print(f"\nSelected project: {selected_project_name}")

selected_project = projects_df[projects_df['project_name'] == selected_project_name].iloc[0]
project_id = selected_project['id']

print(f"Project ID: {project_id}")
print(f"Project ID type: {type(project_id)}")

# Test get_observations_by_project with the numpy.int64 value
print("\nCalling get_observations_by_project()...")
observations_df = db.get_observations_by_project(project_id)

print(f"✅ SUCCESS: Retrieved {len(observations_df)} observations")

if len(observations_df) > 0:
    print("\nSample observations:")
    print(observations_df[['observation_date', 'champion_name', 'overall_status', 'readiness_score']].head(3))
else:
    print("❌ FAILED: Still returning 0 observations")

# Test all projects
print("\n" + "=" * 80)
print("TESTING ALL PROJECTS")
print("=" * 80)

for _, project in projects_df.iterrows():
    project_id = project['id']
    project_name = project['project_name']
    
    obs_df = db.get_observations_by_project(project_id)
    print(f"Project {project_id} ({project_name}): {len(obs_df)} observations")

print("\n" + "=" * 80)
print("FIX VERIFICATION COMPLETE")
print("=" * 80)
