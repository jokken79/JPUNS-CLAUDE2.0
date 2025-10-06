"""
Fix Employee table foreign key from uns_id to rirekisho_id
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def fix_employee_foreign_key():
    """Update Employee table to use rirekisho_id instead of uns_id"""

    migration_sql = """
    -- Drop the old foreign key constraint
    ALTER TABLE employees DROP CONSTRAINT IF EXISTS employees_uns_id_fkey;

    -- Rename the column
    ALTER TABLE employees RENAME COLUMN uns_id TO rirekisho_id;

    -- Add the new foreign key constraint
    ALTER TABLE employees ADD CONSTRAINT employees_rirekisho_id_fkey
        FOREIGN KEY (rirekisho_id) REFERENCES candidates(rirekisho_id);

    -- Add photo_url column if it doesn't exist
    ALTER TABLE employees ADD COLUMN IF NOT EXISTS photo_url VARCHAR(255);
    """

    print("Fixing Employee table foreign key...")

    try:
        with engine.connect() as conn:
            # Execute migration
            conn.execute(text(migration_sql))
            conn.commit()
            print("\n✓ Migration completed successfully!")
            print("Employee table now uses rirekisho_id instead of uns_id")
            print("Photo URL column added to employees table")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    fix_employee_foreign_key()
