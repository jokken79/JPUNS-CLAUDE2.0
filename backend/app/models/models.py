"""
SQLAlchemy Models for UNS-ClaudeJP 1.0
"""
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, Date, Time, Numeric, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


# ============================================
# ENUMS
# ============================================

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    EMPLOYEE = "employee"


class CandidateStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    HIRED = "hired"


class DocumentType(str, enum.Enum):
    RIREKISHO = "rirekisho"
    ZAIRYU_CARD = "zairyu_card"
    LICENSE = "license"
    CONTRACT = "contract"
    OTHER = "other"


class RequestType(str, enum.Enum):
    YUKYU = "yukyu"
    HANKYU = "hankyu"
    IKKIKOKOKU = "ikkikokoku"
    TAISHA = "taisha"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ShiftType(str, enum.Enum):
    ASA = "asa"  # 朝番
    HIRU = "hiru"  # 昼番
    YORU = "yoru"  # 夜番
    OTHER = "other"


# ============================================
# MODELS
# ============================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    uns_id = Column(String(20), unique=True, nullable=False, index=True)
    full_name_kanji = Column(String(100))
    full_name_kana = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(String(10))
    nationality = Column(String(50))
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    photo_url = Column(String(255))
    status = Column(SQLEnum(CandidateStatus), default=CandidateStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))

    # Relationships
    documents = relationship("Document", back_populates="candidate", foreign_keys="Document.candidate_id")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"))
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"))
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    ocr_data = Column(JSON)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    candidate = relationship("Candidate", back_populates="documents", foreign_keys=[candidate_id])
    employee = relationship("Employee", back_populates="documents", foreign_keys=[employee_id])


class Factory(Base):
    __tablename__ = "factories"

    id = Column(Integer, primary_key=True, index=True)
    factory_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    contact_person = Column(String(100))
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employees = relationship("Employee", back_populates="factory")


class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True)
    apartment_code = Column(String(50), unique=True, nullable=False)
    address = Column(Text, nullable=False)
    monthly_rent = Column(Integer, nullable=False)
    capacity = Column(Integer)
    is_available = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employees = relationship("Employee", back_populates="apartment")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    hakenmoto_id = Column(Integer, unique=True, nullable=False, index=True)
    uns_id = Column(String(20), ForeignKey("candidates.uns_id"))
    factory_id = Column(String(20), ForeignKey("factories.factory_id"))
    hakensaki_shain_id = Column(String(50))

    # Personal information
    full_name_kanji = Column(String(100), nullable=False)
    full_name_kana = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(String(10))
    nationality = Column(String(50))
    zairyu_card_number = Column(String(50))
    zairyu_expire_date = Column(Date)

    # Contact information
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    emergency_contact = Column(String(100))
    emergency_phone = Column(String(20))

    # Employment information
    hire_date = Column(Date)
    jikyu = Column(Integer, nullable=False)  # 時給
    position = Column(String(100))
    contract_type = Column(String(50))

    # Financial information
    hourly_rate_charged = Column(Integer)  # 請求単価
    profit_difference = Column(Integer)    # 差額利益
    standard_compensation = Column(Integer)  # 標準報酬
    health_insurance = Column(Integer)     # 健康保険
    nursing_insurance = Column(Integer)    # 介護保険
    pension_insurance = Column(Integer)    # 厚生年金
    social_insurance_date = Column(Date)   # 社保加入日

    # Visa and documents
    visa_type = Column(String(50))         # ビザ種類
    license_type = Column(String(100))     # 免許種類
    license_expire_date = Column(Date)     # 免許期限
    commute_method = Column(String(50))    # 通勤方法
    optional_insurance_expire = Column(Date)  # 任意保険期限
    japanese_level = Column(String(50))    # 日本語検定
    career_up_5years = Column(Boolean, default=False)  # キャリアアップ5年目
    entry_request_date = Column(Date)      # 入社依頼日
    photo_url = Column(String(255))        # 写真URL
    notes = Column(Text)                   # 備考
    postal_code = Column(String(10))       # 郵便番号

    # Apartment
    apartment_id = Column(Integer, ForeignKey("apartments.id"))
    apartment_start_date = Column(Date)
    apartment_move_out_date = Column(Date) # 退去日
    apartment_rent = Column(Integer)

    # Yukyu (有給休暇)
    yukyu_total = Column(Integer, default=0)
    yukyu_used = Column(Integer, default=0)
    yukyu_remaining = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    termination_date = Column(Date)
    termination_reason = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    factory = relationship("Factory", back_populates="employees")
    apartment = relationship("Apartment", back_populates="employees")
    documents = relationship("Document", back_populates="employee", foreign_keys="Document.employee_id")
    timer_cards = relationship("TimerCard", back_populates="employee")
    salary_calculations = relationship("SalaryCalculation", back_populates="employee")
    requests = relationship("Request", back_populates="employee")
    contracts = relationship("Contract", back_populates="employee")


class TimerCard(Base):
    __tablename__ = "timer_cards"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    factory_id = Column(String(20), ForeignKey("factories.factory_id"))
    work_date = Column(Date, nullable=False)

    # Schedules
    clock_in = Column(Time)
    clock_out = Column(Time)
    break_minutes = Column(Integer, default=0)

    # Calculated hours
    regular_hours = Column(Numeric(5, 2), default=0)
    overtime_hours = Column(Numeric(5, 2), default=0)
    night_hours = Column(Numeric(5, 2), default=0)
    holiday_hours = Column(Numeric(5, 2), default=0)

    # Shift type
    shift_type = Column(SQLEnum(ShiftType))

    # Notes
    notes = Column(Text)
    is_approved = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="timer_cards")


class SalaryCalculation(Base):
    __tablename__ = "salary_calculations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    # Hours
    total_regular_hours = Column(Numeric(5, 2))
    total_overtime_hours = Column(Numeric(5, 2))
    total_night_hours = Column(Numeric(5, 2))
    total_holiday_hours = Column(Numeric(5, 2))

    # Payments
    base_salary = Column(Integer)
    overtime_pay = Column(Integer)
    night_pay = Column(Integer)
    holiday_pay = Column(Integer)
    bonus = Column(Integer, default=0)
    gasoline_allowance = Column(Integer, default=0)

    # Deductions
    apartment_deduction = Column(Integer, default=0)
    other_deductions = Column(Integer, default=0)

    # Total
    gross_salary = Column(Integer)
    net_salary = Column(Integer)

    # Company profit
    factory_payment = Column(Integer)  # 時給単価 total
    company_profit = Column(Integer)

    is_paid = Column(Boolean, default=False)
    paid_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="salary_calculations")


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    request_type = Column(SQLEnum(RequestType), nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING)

    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Numeric(3, 1))  # For 半日 can be 0.5

    # Details
    reason = Column(Text)
    notes = Column(Text)

    # Approval
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="requests")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    contract_type = Column(String(50), nullable=False)
    contract_number = Column(String(50), unique=True)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    pdf_path = Column(String(500))
    signed = Column(Boolean, default=False)
    signed_at = Column(DateTime(timezone=True))
    signature_data = Column(Text)  # Base64 signature

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="contracts")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    table_name = Column(String(50))
    record_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
