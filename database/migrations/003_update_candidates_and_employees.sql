-- Migration 003: Update candidates table to use rirekisho_id and update employees

-- Step 1: Rename uns_id to rirekisho_id in candidates table
ALTER TABLE candidates RENAME COLUMN uns_id TO rirekisho_id;

-- Step 2: Add all missing columns to candidates table
ALTER TABLE candidates
ADD COLUMN IF NOT EXISTS reception_date DATE,
ADD COLUMN IF NOT EXISTS arrival_date DATE,
ADD COLUMN IF NOT EXISTS full_name_roman VARCHAR(100),
ADD COLUMN IF NOT EXISTS marital_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS hire_date DATE,
ADD COLUMN IF NOT EXISTS current_address TEXT,
ADD COLUMN IF NOT EXISTS postal_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS prefecture VARCHAR(50),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS town VARCHAR(100),
ADD COLUMN IF NOT EXISTS building VARCHAR(100),
ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS contact_email VARCHAR(100),
ADD COLUMN IF NOT EXISTS home_country_address TEXT,
ADD COLUMN IF NOT EXISTS home_country_phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS home_country_emergency_contact VARCHAR(100),
ADD COLUMN IF NOT EXISTS home_country_emergency_phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS home_country_emergency_relation VARCHAR(50),
ADD COLUMN IF NOT EXISTS zairyu_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS zairyu_card_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS zairyu_expire_date DATE,
ADD COLUMN IF NOT EXISTS visa_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS visa_duration VARCHAR(20),
ADD COLUMN IF NOT EXISTS visa_expire_date DATE,
ADD COLUMN IF NOT EXISTS visa_update_count INTEGER,
ADD COLUMN IF NOT EXISTS visa_category VARCHAR(50),
ADD COLUMN IF NOT EXISTS immigration_history TEXT,
ADD COLUMN IF NOT EXISTS has_driver_license VARCHAR(10),
ADD COLUMN IF NOT EXISTS license_type VARCHAR(100),
ADD COLUMN IF NOT EXISTS license_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS license_issue_date DATE,
ADD COLUMN IF NOT EXISTS license_expire_date DATE,
ADD COLUMN IF NOT EXISTS my_number_card VARCHAR(50),
ADD COLUMN IF NOT EXISTS residence_card_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS health_insurance_card VARCHAR(50),
ADD COLUMN IF NOT EXISTS pension_book VARCHAR(50),
ADD COLUMN IF NOT EXISTS bank_account_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS bank_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS bank_branch VARCHAR(100),
ADD COLUMN IF NOT EXISTS bank_account_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS bank_account_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS job_history_1_company VARCHAR(100),
ADD COLUMN IF NOT EXISTS job_history_1_period VARCHAR(100),
ADD COLUMN IF NOT EXISTS job_history_1_position VARCHAR(100),
ADD COLUMN IF NOT EXISTS job_history_2_company VARCHAR(100),
ADD COLUMN IF NOT EXISTS job_history_2_period VARCHAR(100),
ADD COLUMN IF NOT EXISTS job_history_2_position VARCHAR(100),
ADD COLUMN IF NOT EXISTS job_history_3_company VARCHAR(100),
ADD COLUMN IF NOT EXISTS job_history_3_period VARCHAR(100),
ADD COLUMN IF NOT EXISTS job_history_3_position VARCHAR(100),
ADD COLUMN IF NOT EXISTS japan_work_history_1 VARCHAR(200),
ADD COLUMN IF NOT EXISTS japan_work_history_2 VARCHAR(200),
ADD COLUMN IF NOT EXISTS japan_work_history_3 VARCHAR(200),
ADD COLUMN IF NOT EXISTS skill_1 VARCHAR(100),
ADD COLUMN IF NOT EXISTS skill_2 VARCHAR(100),
ADD COLUMN IF NOT EXISTS skill_3 VARCHAR(100),
ADD COLUMN IF NOT EXISTS skill_4 VARCHAR(100),
ADD COLUMN IF NOT EXISTS interview_result VARCHAR(20),
ADD COLUMN IF NOT EXISTS antigen_test_kit VARCHAR(20),
ADD COLUMN IF NOT EXISTS antigen_test_date DATE,
ADD COLUMN IF NOT EXISTS covid_vaccine_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS language_skill_exists VARCHAR(10),
ADD COLUMN IF NOT EXISTS language_skill_1 VARCHAR(100),
ADD COLUMN IF NOT EXISTS language_skill_2 VARCHAR(100),
ADD COLUMN IF NOT EXISTS japanese_qualification VARCHAR(50),
ADD COLUMN IF NOT EXISTS japanese_level VARCHAR(10),
ADD COLUMN IF NOT EXISTS jlpt_taken VARCHAR(10),
ADD COLUMN IF NOT EXISTS jlpt_date DATE,
ADD COLUMN IF NOT EXISTS jlpt_score INTEGER,
ADD COLUMN IF NOT EXISTS jlpt_scheduled VARCHAR(10),
ADD COLUMN IF NOT EXISTS qualification_1 VARCHAR(100),
ADD COLUMN IF NOT EXISTS qualification_2 VARCHAR(100),
ADD COLUMN IF NOT EXISTS qualification_3 VARCHAR(100),
ADD COLUMN IF NOT EXISTS major VARCHAR(100),
ADD COLUMN IF NOT EXISTS blood_type VARCHAR(5),
ADD COLUMN IF NOT EXISTS dominant_hand VARCHAR(10),
ADD COLUMN IF NOT EXISTS allergy_exists VARCHAR(10),
ADD COLUMN IF NOT EXISTS listening_level VARCHAR(20),
ADD COLUMN IF NOT EXISTS speaking_level VARCHAR(20),
ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS emergency_contact_relation VARCHAR(50),
ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS safety_shoes VARCHAR(10),
ADD COLUMN IF NOT EXISTS read_katakana VARCHAR(20),
ADD COLUMN IF NOT EXISTS read_hiragana VARCHAR(20),
ADD COLUMN IF NOT EXISTS read_kanji VARCHAR(20),
ADD COLUMN IF NOT EXISTS write_katakana VARCHAR(20),
ADD COLUMN IF NOT EXISTS write_hiragana VARCHAR(20),
ADD COLUMN IF NOT EXISTS write_kanji VARCHAR(20),
ADD COLUMN IF NOT EXISTS can_speak VARCHAR(20),
ADD COLUMN IF NOT EXISTS can_understand VARCHAR(20),
ADD COLUMN IF NOT EXISTS can_read_kana VARCHAR(20),
ADD COLUMN IF NOT EXISTS can_write_kana VARCHAR(20);

-- Step 3: Add rirekisho_id column to employees
ALTER TABLE employees
ADD COLUMN IF NOT EXISTS rirekisho_id VARCHAR(20);

-- Step 4: Add foreign key constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_employees_rirekisho'
    ) THEN
        ALTER TABLE employees
        ADD CONSTRAINT fk_employees_rirekisho
        FOREIGN KEY (rirekisho_id) REFERENCES candidates(rirekisho_id);
    END IF;
END $$;

-- Step 5: Create index for performance
CREATE INDEX IF NOT EXISTS idx_employees_rirekisho_id ON employees(rirekisho_id);
