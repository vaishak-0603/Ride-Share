"""
Cleanup script for Git upload
Removes temporary and unnecessary files before committing to Git
"""

import os
import shutil

# Files to delete
files_to_delete = [
    'fix_google_maps.py',
    'fix_offer_ride_map.py',
    'map_routes.py',  # Already integrated into app.py
    'migrate_map_features.py',  # One-time migration script
    'static/js/maps.js.old',
]

# Directories to delete (if empty or unnecessary)
dirs_to_clean = [
    '__pycache__',
]

print("🧹 Cleaning up project for Git upload...\n")

# Delete files
for file in files_to_delete:
    if os.path.exists(file):
        os.remove(file)
        print(f"✅ Deleted: {file}")
    else:
        print(f"⏭️  Skipped (not found): {file}")

# Clean directories
for dir_path in dirs_to_clean:
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        print(f"✅ Deleted directory: {dir_path}")

print("\n✨ Cleanup complete!")
print("\n📋 Next steps:")
print("1. Review .gitignore file")
print("2. Initialize Git: git init")
print("3. Add files: git add .")
print("4. Commit: git commit -m 'Initial commit - Carpooling app with Leaflet maps'")
print("5. Add remote: git remote add origin <your-repo-url>")
print("6. Push: git push -u origin main")
print("\n⚠️  IMPORTANT: Make sure .env is in .gitignore (it contains API keys!)")
