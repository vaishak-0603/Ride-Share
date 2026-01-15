from app import app, db

def fix_sequences():
    """Fix PostgreSQL sequences after data import."""
    with app.app_context():
        tables = ['user', 'car', 'ride', 'booking', 'review', 'wallet', 'expense']
        
        for table in tables:
            try:
                # Get the maximum ID from the table
                result = db.session.execute(db.text(f'SELECT MAX(id) FROM "{table}"'))
                max_id = result.scalar()
                
                if max_id:
                    # Reset the sequence to max_id + 1
                    db.session.execute(db.text(f'SELECT setval(\'{table}_id_seq\', {max_id})'))
                    print(f"Fixed sequence for {table}: set to {max_id}")
            except Exception as e:
                print(f"Could not fix sequence for {table}: {e}")
        
        db.session.commit()
        print("All sequences fixed!")

if __name__ == "__main__":
    fix_sequences()
