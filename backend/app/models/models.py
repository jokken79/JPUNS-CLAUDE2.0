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
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    COORDINATOR = "COORDINATOR"
    EMPLOYEE = "EMPLOYEE"


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
    role = Column(SQLEnum(UserRole, name='user_role'), nullable=False, default=UserRole.EMPLOYEE)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Candidate(Base):
    """履歴書 (Rirekisho) - Resume/CV Table with complete fields"""
    __tablename__ = "candidates"

    # Primary Key & IDs
    id = Column(Integer, primary_key=True, index=True)
    rirekisho_id = Column(String(20), unique=True, nullable=False, index=True)  # 履歴書ID

    # 受付日・来日 (Reception & Arrival Dates)
    reception_date = Column(Date)  # 受付日
    arrival_date = Column(Date)  # 来日

    # 基本情報 (Basic Information)
    full_name_kanji = Column(String(100))  # 氏名
    full_name_kana = Column(String(100))  # フリガナ
    full_name_roman = Column(String(100))  # 氏名（ローマ字)
    gender = Column(String(10))  # 性別
    date_of_birth = Column(Date)  # 生年月日
    photo_url = Column(String(255))  # 写真
    nationality = Column(String(50))  # 国籍
    marital_status = Column(String(20))  # 配偶者
    hire_date = Column(Date)  # 入社日

    # 住所情報 (Address Information)
    postal_code = Column(String(10))  # 郵便番号
    current_address = Column(Text)  # 現住所
    address_banchi = Column(String(100))  # 番地
    building_name = Column(String(100))  # 物件名
    registered_address = Column(Text)  # 登録住所

    # 連絡先 (Contact Information)
    phone = Column(String(20))  # 電話番号
    mobile = Column(String(20))  # 携帯電話

    # パスポート情報 (Passport Information)
    passport_number = Column(String(50))  # パスポート番号
    passport_expiry = Column(Date)  # パスポート期限

    # 在留カード情報 (Residence Card Information)
    residence_status = Column(String(50))  # 在留資格
    residence_expiry = Column(Date)  # （在留カード記載）在留期限
    residence_card_number = Column(String(50))  # 在留カード番号

    # 運転免許情報 (Driver's License Information)
    license_number = Column(String(50))  # 運転免許番号及び条件
    license_expiry = Column(Date)  # 運転免許期限
    car_ownership = Column(String(10))  # 自動車所有
    voluntary_insurance = Column(String(10))  # 任意保険加入

    # 資格・免許 (Qualifications & Licenses)
    forklift_license = Column(String(10))  # ﾌｫｰｸﾘﾌﾄ免許
    tama_kake = Column(String(10))  # 玉掛
    mobile_crane_under_5t = Column(String(10))  # 移動式ｸﾚｰﾝ運転士(5ﾄﾝ未満)
    mobile_crane_over_5t = Column(String(10))  # 移動式ｸﾚｰﾝ運転士(5ﾄﾝ以上)
    gas_welding = Column(String(10))  # ｶﾞｽ溶接作業者

    # 家族構成 (Family Members) - Member 1
    family_name_1 = Column(String(100))  # 家族構成氏名1
    family_relation_1 = Column(String(50))  # 家族構成続柄1
    family_age_1 = Column(Integer)  # 年齢1
    family_residence_1 = Column(String(50))  # 居住1
    family_separate_address_1 = Column(Text)  # 別居住住所1

    # 家族構成 - Member 2
    family_name_2 = Column(String(100))  # 家族構成氏名2
    family_relation_2 = Column(String(50))  # 家族構成続柄2
    family_age_2 = Column(Integer)  # 年齢2
    family_residence_2 = Column(String(50))  # 居住2
    family_separate_address_2 = Column(Text)  # 別居住住所2

    # 家族構成 - Member 3
    family_name_3 = Column(String(100))  # 氏名3
    family_relation_3 = Column(String(50))  # 家族構成続柄3
    family_age_3 = Column(Integer)  # 年齢3
    family_residence_3 = Column(String(50))  # 居住3
    family_separate_address_3 = Column(Text)  # 別居住住所3

    # 家族構成 - Member 4
    family_name_4 = Column(String(100))  # 家族構成氏名4
    family_relation_4 = Column(String(50))  # 家族構成続柄4
    family_age_4 = Column(Integer)  # 年齢4
    family_residence_4 = Column(String(50))  # 居住4
    family_separate_address_4 = Column(Text)  # 別居住住所4

    # 家族構成 - Member 5
    family_name_5 = Column(String(100))  # 家族構成氏名5
    family_relation_5 = Column(String(50))  # 家族構成続柄5
    family_age_5 = Column(Integer)  # 年齢5
    family_residence_5 = Column(String(50))  # 居住5
    family_separate_address_5 = Column(Text)  # 別居住住所5

    # 職歴 (Work History) - Entry 7 (as per your column list)
    work_history_company_7 = Column(String(200))  # 家族構成社社7
    work_history_entry_company_7 = Column(String(200))  # 職歴入社会社名7
    work_history_exit_company_7 = Column(String(200))  # 職歴退社会社名7

    # 経験作業 (Work Experience)
    exp_nc_lathe = Column(String(10))  # NC旋盤
    exp_lathe = Column(String(10))  # 旋盤
    exp_press = Column(String(10))  # ﾌﾟﾚｽ
    exp_forklift = Column(String(10))  # ﾌｫｰｸﾘﾌﾄ
    exp_packing = Column(String(10))  # 梱包
    exp_welding = Column(String(10))  # 溶接
    exp_car_assembly = Column(String(10))  # 車部品組立
    exp_car_line = Column(String(10))  # 車部品ライン
    exp_car_inspection = Column(String(10))  # 車部品検査
    exp_electronic_inspection = Column(String(10))  # 電子部品検査
    exp_food_processing = Column(String(10))  # 食品加工
    exp_casting = Column(String(10))  # 鋳造
    exp_line_leader = Column(String(10))  # ラインリーダー
    exp_painting = Column(String(10))  # 塗装
    exp_other = Column(Text)  # その他

    # お弁当 (Lunch/Bento Options)
    bento_lunch_dinner = Column(String(10))  # お弁当　昼/夜
    bento_lunch_only = Column(String(10))  # お弁当　昼のみ
    bento_dinner_only = Column(String(10))  # お弁当　夜のみ
    bento_bring_own = Column(String(10))  # お弁当　持参

    # 通勤 (Commute)
    commute_method = Column(String(50))  # 通勤方法
    commute_time_oneway = Column(Integer)  # 通勤片道時間

    # 面接・検査 (Interview & Tests)
    interview_result = Column(String(20))  # 面接結果OK
    antigen_test_kit = Column(String(20))  # 簡易抗原検査キット
    antigen_test_date = Column(Date)  # 簡易抗原検査実施日
    covid_vaccine_status = Column(String(50))  # コロナワクチン予防接種状態

    # 語学スキル (Language Skills)
    language_skill_exists = Column(String(10))  # 語学スキル有無
    language_skill_1 = Column(String(100))  # 語学スキル有無１
    language_skill_2 = Column(String(100))  # 語学スキル有無2

    # 日本語能力 (Japanese Language Ability)
    japanese_qualification = Column(String(50))  # 日本語能力資格
    japanese_level = Column(String(10))  # 日本語能力資格Level
    jlpt_taken = Column(String(10))  # 能力試験受験
    jlpt_date = Column(Date)  # 能力試験受験日付
    jlpt_score = Column(Integer)  # 能力試験受験点数
    jlpt_scheduled = Column(String(10))  # 能力試験受験受験予定

    # 有資格 (Qualifications)
    qualification_1 = Column(String(100))  # 有資格取得
    qualification_2 = Column(String(100))  # 有資格取得1
    qualification_3 = Column(String(100))  # 有資格取得2

    # 学歴 (Education)
    major = Column(String(100))  # 専攻

    # 身体情報 (Physical Information)
    blood_type = Column(String(5))  # 血液型
    dominant_hand = Column(String(10))  # 利き腕
    allergy_exists = Column(String(10))  # アレルギー有無

    # 日本語能力詳細 (Japanese Ability Details)
    listening_level = Column(String(20))  # 聞く選択
    speaking_level = Column(String(20))  # 話す選択

    # 緊急連絡先 (Emergency Contact)
    emergency_contact_name = Column(String(100))  # 緊急連絡先　氏名
    emergency_contact_relation = Column(String(50))  # 緊急連絡先　続柄
    emergency_contact_phone = Column(String(20))  # 緊急連絡先　電話番号

    # 作業用品 (Work Equipment)
    safety_shoes = Column(String(10))  # 安全靴

    # 読み書き能力 (Reading & Writing Ability)
    read_katakana = Column(String(20))  # 読む　カナ
    read_hiragana = Column(String(20))  # 読む　ひら
    read_kanji = Column(String(20))  # 読む　漢字
    write_katakana = Column(String(20))  # 書く　カナ
    write_hiragana = Column(String(20))  # 書く　ひら
    write_kanji = Column(String(20))  # 書く　漢字氏名3

    # 会話能力 (Conversation Ability)
    can_speak = Column(String(20))  # 会話ができる
    can_understand = Column(String(20))  # 会話が理解できる
    can_read_kana = Column(String(20))  # ひらがな・カタカナ読める
    can_write_kana = Column(String(20))  # ひらがな・カタカナ書け

    # Legacy fields for compatibility
    email = Column(String(100))
    # phone y address ya están definidos arriba, no duplicar

    # Status & Audit Fields
    status = Column(SQLEnum(CandidateStatus, name='candidate_status'), default=CandidateStatus.PENDING)
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
    document_type = Column(SQLEnum(DocumentType, name='document_type'), nullable=False)
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
    rirekisho_id = Column(String(20), ForeignKey("candidates.rirekisho_id"))  # Changed from uns_id
    factory_id = Column(String(20), ForeignKey("factories.factory_id"))
    hakensaki_shain_id = Column(String(50))

    # Personal information
    full_name_kanji = Column(String(100), nullable=False)
    full_name_kana = Column(String(100))
    photo_url = Column(String(255))  # Photo from candidate
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
    # photo_url ya está definido arriba, no duplicar
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
    shift_type = Column(SQLEnum(ShiftType, name='shift_type'))

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
    request_type = Column(SQLEnum(RequestType, name='request_type'), nullable=False)
    status = Column(SQLEnum(RequestStatus, name='request_status'), default=RequestStatus.PENDING)

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
