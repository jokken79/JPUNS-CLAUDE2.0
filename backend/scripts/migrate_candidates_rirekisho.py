"""
Migration script to add all rirekisho (履歴書) fields to candidates table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def migrate_candidates_table():
    """Add all rirekisho fields to candidates table"""

    migration_sql = """
    -- Rename uns_id to rirekisho_id
    ALTER TABLE candidates RENAME COLUMN uns_id TO rirekisho_id;

    -- 受付日・来日 (Reception & Arrival Dates)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS reception_date DATE;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS arrival_date DATE;

    -- 基本情報 (Basic Information) - Add missing fields
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS full_name_roman VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS marital_status VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS hire_date DATE;

    -- 住所情報 (Address Information)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS postal_code VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS current_address TEXT;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS address_banchi VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS building_name VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS registered_address TEXT;

    -- 連絡先 (Contact Information)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS mobile VARCHAR(20);

    -- パスポート情報 (Passport Information)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS passport_number VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS passport_expiry DATE;

    -- 在留カード情報 (Residence Card Information)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS residence_status VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS residence_expiry DATE;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS residence_card_number VARCHAR(50);

    -- 運転免許情報 (Driver's License Information)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS license_number VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS license_expiry DATE;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS car_ownership VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS voluntary_insurance VARCHAR(10);

    -- 資格・免許 (Qualifications & Licenses)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS forklift_license VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS tama_kake VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS mobile_crane_under_5t VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS mobile_crane_over_5t VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS gas_welding VARCHAR(10);

    -- 家族構成 (Family Members) - Member 1
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_name_1 VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_relation_1 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_age_1 INTEGER;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_residence_1 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_separate_address_1 TEXT;

    -- 家族構成 - Member 2
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_name_2 VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_relation_2 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_age_2 INTEGER;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_residence_2 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_separate_address_2 TEXT;

    -- 家族構成 - Member 3
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_name_3 VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_relation_3 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_age_3 INTEGER;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_residence_3 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_separate_address_3 TEXT;

    -- 家族構成 - Member 4
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_name_4 VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_relation_4 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_age_4 INTEGER;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_residence_4 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_separate_address_4 TEXT;

    -- 家族構成 - Member 5
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_name_5 VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_relation_5 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_age_5 INTEGER;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_residence_5 VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS family_separate_address_5 TEXT;

    -- 職歴 (Work History)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS work_history_company_7 VARCHAR(200);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS work_history_entry_company_7 VARCHAR(200);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS work_history_exit_company_7 VARCHAR(200);

    -- 経験作業 (Work Experience)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_nc_lathe VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_lathe VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_press VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_forklift VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_packing VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_welding VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_car_assembly VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_car_line VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_car_inspection VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_electronic_inspection VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_food_processing VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_casting VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_line_leader VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_painting VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS exp_other TEXT;

    -- お弁当 (Lunch/Bento Options)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS bento_lunch_dinner VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS bento_lunch_only VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS bento_dinner_only VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS bento_bring_own VARCHAR(10);

    -- 通勤 (Commute)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS commute_method VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS commute_time_oneway INTEGER;

    -- 面接・検査 (Interview & Tests)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS interview_result VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS antigen_test_kit VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS antigen_test_date DATE;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS covid_vaccine_status VARCHAR(50);

    -- 語学スキル (Language Skills)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS language_skill_exists VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS language_skill_1 VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS language_skill_2 VARCHAR(100);

    -- 日本語能力 (Japanese Language Ability)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS japanese_qualification VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS japanese_level VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS jlpt_taken VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS jlpt_date DATE;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS jlpt_score INTEGER;
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS jlpt_scheduled VARCHAR(10);

    -- 有資格 (Qualifications)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS qualification_1 VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS qualification_2 VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS qualification_3 VARCHAR(100);

    -- 学歴 (Education)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS major VARCHAR(100);

    -- 身体情報 (Physical Information)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS blood_type VARCHAR(5);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS dominant_hand VARCHAR(10);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS allergy_exists VARCHAR(10);

    -- 日本語能力詳細 (Japanese Ability Details)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS listening_level VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS speaking_level VARCHAR(20);

    -- 緊急連絡先 (Emergency Contact)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(100);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS emergency_contact_relation VARCHAR(50);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20);

    -- 作業用品 (Work Equipment)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS safety_shoes VARCHAR(10);

    -- 読み書き能力 (Reading & Writing Ability)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS read_katakana VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS read_hiragana VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS read_kanji VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS write_katakana VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS write_hiragana VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS write_kanji VARCHAR(20);

    -- 会話能力 (Conversation Ability)
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS can_speak VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS can_understand VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS can_read_kana VARCHAR(20);
    ALTER TABLE candidates ADD COLUMN IF NOT EXISTS can_write_kana VARCHAR(20);
    """

    print("Starting migration to add rirekisho fields to candidates table...")

    try:
        with engine.connect() as conn:
            # Split by semicolon and execute each ALTER TABLE statement
            statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]

            for statement in statements:
                if statement:
                    try:
                        conn.execute(text(statement))
                        print(f"✓ Executed: {statement[:80]}...")
                    except Exception as e:
                        # Ignore errors for columns that already exist
                        if 'already exists' in str(e).lower() or 'duplicate column' in str(e).lower():
                            print(f"⊘ Column already exists, skipping: {statement[:80]}...")
                        else:
                            print(f"✗ Error: {e}")
                            raise

            conn.commit()
            print("\n✓ Migration completed successfully!")
            print("Candidates table now has all rirekisho (履歴書) fields.")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_candidates_table()
