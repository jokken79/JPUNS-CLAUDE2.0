"""
Check and fix column names in candidates and employees tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.core.database import engine

def check_and_fix_columns():
    """Check columns and fix if needed"""

    print("Checking table structures...")

    try:
        with engine.connect() as conn:
            # Check if candidates has uns_id or rirekisho_id
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'candidates'
                AND column_name IN ('uns_id', 'rirekisho_id');
            """))

            columns = [row[0] for row in result]
            print(f"Candidates columns found: {columns}")

            if 'uns_id' in columns and 'rirekisho_id' not in columns:
                print("\n→ Renaming candidates.uns_id to rirekisho_id...")
                conn.execute(text("ALTER TABLE candidates RENAME COLUMN uns_id TO rirekisho_id;"))
                conn.commit()
                print("✓ Renamed candidates.uns_id to rirekisho_id")
            elif 'rirekisho_id' in columns:
                print("✓ candidates.rirekisho_id already exists")

            # Check employees table
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'employees'
                AND column_name IN ('uns_id', 'rirekisho_id', 'photo_url');
            """))

            emp_columns = [row[0] for row in result]
            print(f"\nEmployees columns found: {emp_columns}")

            if 'uns_id' in emp_columns and 'rirekisho_id' not in emp_columns:
                print("\n→ Updating employees table...")

                # Drop old constraint
                conn.execute(text("ALTER TABLE employees DROP CONSTRAINT IF EXISTS employees_uns_id_fkey;"))
                print("✓ Dropped old foreign key constraint")

                # Rename column
                conn.execute(text("ALTER TABLE employees RENAME COLUMN uns_id TO rirekisho_id;"))
                print("✓ Renamed employees.uns_id to rirekisho_id")

                # Add new constraint
                conn.execute(text("""
                    ALTER TABLE employees ADD CONSTRAINT employees_rirekisho_id_fkey
                        FOREIGN KEY (rirekisho_id) REFERENCES candidates(rirekisho_id);
                """))
                print("✓ Added new foreign key constraint")

                conn.commit()

            # Add photo_url if not exists
            if 'photo_url' not in emp_columns:
                print("\n→ Adding photo_url column to employees...")
                conn.execute(text("ALTER TABLE employees ADD COLUMN photo_url VARCHAR(255);"))
                conn.commit()
                print("✓ Added photo_url column")
            else:
                print("✓ employees.photo_url already exists")

            print("\n✓ All migrations completed successfully!")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    check_and_fix_columns()
