-- UNS-ClaudeJP 1.0 Database Schema
-- PostgreSQL Database Initialization
-- FIXED VERSION: Foreign keys added after table creation

-- ============================================
-- EXTENSIONS
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- ENUM TYPES
-- ============================================

CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'coordinator', 'employee');
CREATE TYPE candidate_status AS ENUM ('pending', 'approved', 'rejected', 'hired');
CREATE TYPE document_type AS ENUM ('rirekisho', 'zairyu_card', 'license', 'contract', 'other');
CREATE TYPE request_type AS ENUM ('yukyu', 'hankyu', 'ikkikokoku', 'taisha');
CREATE TYPE request_status AS ENUM ('pending', 'approved', 'rejected');
CREATE TYPE shift_type AS ENUM ('asa', 'hiru', 'yoru', 'other');

-- ============================================
-- TABLES (No FK constraints initially)
-- ============================================

-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'employee',
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidates Table
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    uns_id VARCHAR(20) UNIQUE NOT NULL,
    full_name_kanji VARCHAR(100),
    full_name_kana VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(10),
    nationality VARCHAR(50),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    photo_url VARCHAR(255),
    status candidate_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP
);

-- Factories Table
CREATE TABLE factories (
    id SERIAL PRIMARY KEY,
    factory_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    contact_person VARCHAR(100),
    config JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Apartments Table
CREATE TABLE apartments (
    id SERIAL PRIMARY KEY,
    apartment_code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    monthly_rent INTEGER NOT NULL,
    capacity INTEGER,
    is_available BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees Table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    hakenmoto_id INTEGER UNIQUE NOT NULL,
    uns_id VARCHAR(20) REFERENCES candidates(uns_id),
    factory_id VARCHAR(20) REFERENCES factories(factory_id),
    hakensaki_shain_id VARCHAR(50),
    full_name_kanji VARCHAR(100) NOT NULL,
    full_name_kana VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(10),
    nationality VARCHAR(50),
    zairyu_card_number VARCHAR(50),
    zairyu_expire_date DATE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    hire_date DATE,
    jikyu INTEGER NOT NULL,
    position VARCHAR(100),
    contract_type VARCHAR(50),
    apartment_id INTEGER REFERENCES apartments(id),
    apartment_start_date DATE,
    apartment_rent INTEGER,
    yukyu_total INTEGER DEFAULT 0,
    yukyu_used INTEGER DEFAULT 0,
    yukyu_remaining INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    termination_date DATE,
    termination_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents Table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    document_type document_type NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    ocr_data JSONB,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER REFERENCES users(id)
);

-- Timer Cards Table
CREATE TABLE timer_cards (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    factory_id VARCHAR(20) REFERENCES factories(factory_id),
    work_date DATE NOT NULL,
    clock_in TIME,
    clock_out TIME,
    break_minutes INTEGER DEFAULT 0,
    regular_hours DECIMAL(5,2) DEFAULT 0,
    overtime_hours DECIMAL(5,2) DEFAULT 0,
    night_hours DECIMAL(5,2) DEFAULT 0,
    holiday_hours DECIMAL(5,2) DEFAULT 0,
    shift_type shift_type,
    notes TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Salary Calculations Table
CREATE TABLE salary_calculations (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    total_regular_hours DECIMAL(5,2),
    total_overtime_hours DECIMAL(5,2),
    total_night_hours DECIMAL(5,2),
    total_holiday_hours DECIMAL(5,2),
    base_salary INTEGER,
    overtime_pay INTEGER,
    night_pay INTEGER,
    holiday_pay INTEGER,
    bonus INTEGER DEFAULT 0,
    gasoline_allowance INTEGER DEFAULT 0,
    apartment_deduction INTEGER DEFAULT 0,
    other_deductions INTEGER DEFAULT 0,
    gross_salary INTEGER,
    net_salary INTEGER,
    factory_payment INTEGER,
    company_profit INTEGER,
    is_paid BOOLEAN DEFAULT FALSE,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Requests Table
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    request_type request_type NOT NULL,
    status request_status DEFAULT 'pending',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days DECIMAL(3,1),
    reason TEXT,
    notes TEXT,
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contracts Table
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    contract_type VARCHAR(50) NOT NULL,
    contract_number VARCHAR(50) UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE,
    pdf_path VARCHAR(500),
    signed BOOLEAN DEFAULT FALSE,
    signed_at TIMESTAMP,
    signature_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Log Table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_candidates_uns_id ON candidates(uns_id);
CREATE INDEX idx_employees_hakenmoto_id ON employees(hakenmoto_id);
CREATE INDEX idx_employees_factory_id ON employees(factory_id);
CREATE INDEX idx_timer_cards_employee_date ON timer_cards(employee_id, work_date);
CREATE INDEX idx_salary_calculations_employee_month ON salary_calculations(employee_id, year, month);
CREATE INDEX idx_requests_employee_status ON requests(employee_id, status);
CREATE INDEX idx_documents_candidate ON documents(candidate_id);
CREATE INDEX idx_documents_employee ON documents(employee_id);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_candidates_updated_at BEFORE UPDATE ON candidates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_factories_updated_at BEFORE UPDATE ON factories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_timer_cards_updated_at BEFORE UPDATE ON timer_cards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_requests_updated_at BEFORE UPDATE ON requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- INITIAL DATA
-- ============================================

INSERT INTO users (username, email, password_hash, role, full_name) VALUES
('admin', 'admin@uns-kikaku.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbW4t.5u2', 'super_admin', 'System Administrator');

CREATE SEQUENCE rirekisho_id_seq START 1000;
CREATE SEQUENCE factory_id_seq START 1;
