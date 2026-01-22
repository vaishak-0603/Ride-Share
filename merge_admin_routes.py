"""
Script to merge admin routes into app.py
This fixes the circular import issue by integrating admin routes directly.
"""

def merge_admin_routes():
    print("Starting admin routes merge...")
    
    # Read app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Read admin routes
    with open('admin_routes.py', 'r', encoding='utf-8') as f:
        admin_routes_content = f.read()
    
    # Extract only the route definitions (skip imports)
    admin_routes_lines = []
    skip_imports = True
    
    for line in admin_routes_content.split('\n'):
        # Skip import statements
        if line.strip().startswith('from app import') or line.strip().startswith('from flask import'):
            continue
        if line.strip().startswith('from functools import'):
            continue
        if line.strip().startswith('from datetime import'):
            continue
        if line.strip().startswith('from sqlalchemy import'):
            continue
        
        # Start capturing after the imports
        if '@app.route' in line or (admin_routes_lines and line):
            admin_routes_lines.append(line)
    
    admin_routes_code = '\n'.join(admin_routes_lines)
    
    # Find the location to insert (before "if __name__ == '__main__':")
    if "if __name__ == '__main__':" in app_content:
        parts = app_content.rsplit("if __name__ == '__main__':", 1)
        
        # Insert admin routes
        new_content = parts[0] + "\n# " + "="*76 + "\n"
        new_content += "# ADMIN PANEL ROUTES\n"
        new_content += "# " + "="*76 + "\n\n"
        new_content += admin_routes_code
        new_content += "\n\n# " + "="*76 + "\n"
        new_content += "# END OF ADMIN ROUTES\n"
        new_content += "# " + "="*76 + "\n\n"
        new_content += "if __name__ == '__main__':" + parts[1]
        
        # Write to app.py
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Admin routes successfully merged into app.py!")
        print("✅ Server needs to be restarted for changes to take effect.")
        return True
    else:
        print("❌ Could not find insertion point in app.py")
        return False

if __name__ == '__main__':
    merge_admin_routes()
