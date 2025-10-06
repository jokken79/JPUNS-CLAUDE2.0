-- Add extended fields to employees table
-- Migration: 002_add_employee_extended_fields

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS hourly_rate_charged INTEGER,  -- 請求単価
ADD COLUMN IF NOT EXISTS profit_difference INTEGER,     -- 差額利益
ADD COLUMN IF NOT EXISTS standard_compensation INTEGER, -- 標準報酬
ADD COLUMN IF NOT EXISTS health_insurance INTEGER,      -- 健康保険
ADD COLUMN IF NOT EXISTS nursing_insurance INTEGER,     -- 介護保険
ADD COLUMN IF NOT EXISTS pension_insurance INTEGER,     -- 厚生年金
ADD COLUMN IF NOT EXISTS visa_type VARCHAR(50),         -- ビザ種類
ADD COLUMN IF NOT EXISTS license_type VARCHAR(100),     -- 免許種類
ADD COLUMN IF NOT EXISTS license_expire_date DATE,      -- 免許期限
ADD COLUMN IF NOT EXISTS commute_method VARCHAR(50),    -- 通勤方法
ADD COLUMN IF NOT EXISTS optional_insurance_expire DATE, -- 任意保険期限
ADD COLUMN IF NOT EXISTS japanese_level VARCHAR(50),    -- 日本語検定
ADD COLUMN IF NOT EXISTS career_up_5years BOOLEAN,      -- キャリアアップ5年目
ADD COLUMN IF NOT EXISTS social_insurance_date DATE,    -- 社保加入日
ADD COLUMN IF NOT EXISTS entry_request_date DATE,       -- 入社依頼日
ADD COLUMN IF NOT EXISTS postal_code VARCHAR(10),       -- 郵便番号
ADD COLUMN IF NOT EXISTS apartment_move_out_date DATE,  -- 退去日
ADD COLUMN IF NOT EXISTS notes TEXT,                    -- 備考
ADD COLUMN IF NOT EXISTS photo_url VARCHAR(255);        -- 写真URL (from rirekisho)

-- Create index for frequently queried fields
CREATE INDEX IF NOT EXISTS idx_employees_visa_expire ON employees(zairyu_expire_date);
CREATE INDEX IF NOT EXISTS idx_employees_license_expire ON employees(license_expire_date);
CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON employees(hire_date);
