"""
Script to import factory and employee data to PostgreSQL
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.insert(0, '/app')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Factory, Employee, ContractWorker, Staff


def import_factories(db: Session):
    """Import factories from JSON files"""
    print("=" * 50)
    print("IMPORTANDO FÁBRICAS")
    print("=" * 50)

    try:
        # Load factories index
        with open('/app/config/factories_index.json', 'r', encoding='utf-8') as f:
            index = json.load(f)

        imported = 0
        skipped = 0

        for factory_info in index['factories']:
            try:
                factory_id = factory_info['factory_id']

                # Check if exists
                existing = db.query(Factory).filter(Factory.factory_id == factory_id).first()
                if existing:
                    skipped += 1
                    continue

                # Load full factory config
                factory_file = Path(f'/app/config/factories/{factory_id}.json')
                with open(factory_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Create factory record
                factory = Factory(
                    factory_id=factory_id,
                    name=f"{config['client_company']['name']} - {config['plant']['name']}".strip(),
                    address=config['plant']['address'],
                    phone=config['plant']['phone'],
                    contact_person=config['assignment']['supervisor']['name'],
                    config=config,
                    is_active=True
                )

                db.add(factory)
                db.commit()  # Commit individually
                imported += 1

                if imported % 20 == 0:
                    print(f"  Procesadas {imported} fábricas...")

            except Exception as e:
                db.rollback()
                print(f"  ✗ Error en {factory_id}: {e}")

        print(f"✓ Importadas {imported} fábricas a PostgreSQL")
        if skipped > 0:
            print(f"  ⚠ {skipped} duplicados omitidos\n")
        return imported

    except Exception as e:
        print(f"✗ Error importando fábricas: {e}\n")
        return 0


def import_haken_employees(db: Session):
    """Import 派遣社員 (Dispatch employees)"""
    print("=" * 50)
    print("IMPORTANDO 派遣社員 (DISPATCH EMPLOYEES)")
    print("=" * 50)

    try:
        df = pd.read_excel('/app/config/employee_master.xlsm', sheet_name='派遣社員', header=1)

        imported = 0
        errors = 0
        skipped = 0

        for idx, row in df.iterrows():
            try:
                # Skip if no employee number
                if pd.isna(row['社員№']):
                    continue

                hakenmoto_id = int(row['社員№'])

                # Check if employee already exists (skip duplicates)
                existing = db.query(Employee).filter(Employee.hakenmoto_id == hakenmoto_id).first()
                if existing:
                    skipped += 1
                    continue

                # Helper function to parse dates safely
                def parse_date(value):
                    if pd.notna(value):
                        try:
                            return pd.to_datetime(value).date()
                        except:
                            pass
                    return None

                # Helper function to parse integers safely
                def parse_int(value):
                    if pd.notna(value):
                        try:
                            return int(float(value))
                        except:
                            pass
                    return None

                # Parse dates
                hire_date = parse_date(row.get('入社日'))
                current_hire_date = parse_date(row.get('現入社'))
                termination_date = parse_date(row.get('退社日'))
                zairyu_expire = parse_date(row.get('ビザ期限'))
                dob = parse_date(row.get('生年月日'))
                jikyu_revision_date = parse_date(row.get('時給改定'))
                billing_revision_date = parse_date(row.get('請求改定'))
                social_insurance_date = parse_date(row.get('社保加入'))
                entry_request_date = parse_date(row.get('入社依頼'))
                license_expire_date = parse_date(row.get('免許期限'))
                optional_insurance_expire = parse_date(row.get('任意保険期限'))
                apartment_start_date = parse_date(row.get('入居'))
                apartment_move_out_date = parse_date(row.get('退去'))

                # Parse status
                is_active = row.get('現在') != '退社' if pd.notna(row.get('現在')) else True

                # Parse integers
                jikyu = parse_int(row.get('時給')) or 0
                hourly_rate_charged = parse_int(row.get('請求単価'))
                profit_difference = parse_int(row.get('差額利益'))
                standard_compensation = parse_int(row.get('標準報酬'))
                health_insurance = parse_int(row.get('健康保険'))
                nursing_insurance = parse_int(row.get('介護保険'))
                pension_insurance = parse_int(row.get('厚生年金'))

                # Parse strings
                def get_str(key):
                    val = row.get(key)
                    return str(val) if pd.notna(val) else None

                # Create employee record with ALL fields
                employee = Employee(
                    hakenmoto_id=hakenmoto_id,
                    factory_id=get_str('派遣先ID'),
                    hakensaki_shain_id=get_str('派遣先社員ID'),
                    full_name_kanji=get_str('氏名') or '',
                    full_name_kana=get_str('カナ') or '',
                    date_of_birth=dob,
                    gender=get_str('性別'),
                    nationality=get_str('国籍'),
                    zairyu_expire_date=zairyu_expire,
                    visa_type=get_str('ビザ種類'),
                    postal_code=get_str('〒'),
                    address=get_str('住所'),
                    phone=None,
                    email=None,
                    # Employment
                    hire_date=hire_date,
                    current_hire_date=current_hire_date,
                    jikyu=jikyu,
                    jikyu_revision_date=jikyu_revision_date,
                    position=get_str('職種'),
                    contract_type='派遣',
                    # Assignment
                    assignment_location=get_str('配属先'),
                    assignment_line=get_str('配属ライン'),
                    job_description=get_str('仕事内容'),
                    # Financial
                    hourly_rate_charged=hourly_rate_charged,
                    billing_revision_date=billing_revision_date,
                    profit_difference=profit_difference,
                    standard_compensation=standard_compensation,
                    health_insurance=health_insurance,
                    nursing_insurance=nursing_insurance,
                    pension_insurance=pension_insurance,
                    social_insurance_date=social_insurance_date,
                    # License
                    license_type=get_str('免許種類'),
                    license_expire_date=license_expire_date,
                    commute_method=get_str('通勤方法'),
                    optional_insurance_expire=optional_insurance_expire,
                    # Skills
                    japanese_level=get_str('日本語検定'),
                    career_up_5years=get_str('キャリアアップ5年目') == 'はい',
                    # Apartment
                    apartment_start_date=apartment_start_date,
                    apartment_move_out_date=apartment_move_out_date,
                    # Other
                    entry_request_date=entry_request_date,
                    notes=get_str('備考'),
                    is_active=is_active,
                    termination_date=termination_date
                )

                db.add(employee)
                db.commit()  # Commit individually
                imported += 1

                if imported % 100 == 0:
                    print(f"  Procesados {imported} empleados...")

            except Exception as e:
                db.rollback()
                errors += 1
                if errors < 10:  # Only show first 10 errors
                    print(f"  ✗ Error en fila {idx}: {e}")
        print(f"✓ Importados {imported} empleados 派遣社員")
        if skipped > 0:
            print(f"  ⚠ {skipped} duplicados omitidos")
        if errors > 0:
            print(f"  ⚠ {errors} errores encontrados\n")
        return imported

    except Exception as e:
        db.rollback()
        print(f"✗ Error importando 派遣社員: {e}\n")
        return 0


def import_ukeoi_employees(db: Session):
    """Import 請負社員 (Contract employees)"""
    print("=" * 50)
    print("IMPORTANDO 請負社員 (CONTRACT EMPLOYEES)")
    print("=" * 50)

    try:
        df = pd.read_excel('/app/config/employee_master.xlsm', sheet_name='請負社員', header=2)

        imported = 0
        errors = 0
        skipped = 0

        for idx, row in df.iterrows():
            try:
                # Get column by index since names might be problematic
                status = row.iloc[0] if len(row) > 0 else None
                shain_no = row.iloc[1] if len(row) > 1 else None

                # Skip if no employee number
                if pd.isna(shain_no):
                    continue

                hakenmoto_id = int(shain_no)

                # Check if already exists
                existing = db.query(ContractWorker).filter(ContractWorker.hakenmoto_id == hakenmoto_id).first()
                if existing:
                    skipped += 1
                    continue

                name = row.iloc[3] if len(row) > 3 else ''
                kana = row.iloc[4] if len(row) > 4 else ''
                gender = row.iloc[5] if len(row) > 5 else None
                nationality = row.iloc[6] if len(row) > 6 else None

                # Jikyu
                jikyu = 0
                if len(row) > 9 and pd.notna(row.iloc[9]):
                    try:
                        jikyu = int(float(row.iloc[9]))
                    except:
                        pass

                # Dates
                hire_date = None
                if len(row) > 25 and pd.notna(row.iloc[25]):
                    try:
                        hire_date = pd.to_datetime(row.iloc[25]).date()
                    except:
                        pass

                termination_date = None
                is_active = status != '退社' if pd.notna(status) else True
                if len(row) > 26 and pd.notna(row.iloc[26]):
                    try:
                        termination_date = pd.to_datetime(row.iloc[26]).date()
                    except:
                        pass

                contract_worker = ContractWorker(
                    hakenmoto_id=hakenmoto_id,
                    full_name_kanji=str(name) if pd.notna(name) else '',
                    full_name_kana=str(kana) if pd.notna(kana) else '',
                    gender=str(gender) if pd.notna(gender) else None,
                    nationality=str(nationality) if pd.notna(nationality) else None,
                    hire_date=hire_date,
                    jikyu=jikyu,
                    contract_type='請負',
                    is_active=is_active,
                    termination_date=termination_date
                )

                db.add(contract_worker)
                db.commit()  # Commit individually
                imported += 1

                if imported % 50 == 0:
                    print(f"  Procesados {imported} empleados...")

            except Exception as e:
                db.rollback()
                errors += 1
                if errors < 10:
                    print(f"  ✗ Error en fila {idx}: {e}")
        print(f"✓ Importados {imported} empleados 請負社員")
        if skipped > 0:
            print(f"  ⚠ {skipped} duplicados omitidos")
        if errors > 0:
            print(f"  ⚠ {errors} errores encontrados\n")
        return imported

    except Exception as e:
        db.rollback()
        print(f"✗ Error importando 請負社員: {e}\n")
        return 0


def import_staff_employees(db: Session):
    """Import スタッフ (Staff employees)"""
    print("=" * 50)
    print("IMPORTANDO スタッフ (STAFF)")
    print("=" * 50)

    try:
        df = pd.read_excel('/app/config/employee_master.xlsm', sheet_name='スタッフ', header=2)

        imported = 0
        errors = 0
        skipped = 0

        for idx, row in df.iterrows():
            try:
                # Get by index
                status = row.iloc[0] if len(row) > 0 else None
                shain_no = row.iloc[1] if len(row) > 1 else None

                if pd.isna(shain_no):
                    continue

                staff_id = int(shain_no)

                # Check if already exists
                existing = db.query(Staff).filter(Staff.staff_id == staff_id).first()
                if existing:
                    skipped += 1
                    continue

                name = row.iloc[2] if len(row) > 2 else ''
                kana = row.iloc[3] if len(row) > 3 else ''

                # Monthly salary (staff typically have monthly salary, not hourly)
                monthly_salary = 0
                if len(row) > 7 and pd.notna(row.iloc[7]):
                    try:
                        monthly_salary = int(float(row.iloc[7]))
                    except:
                        pass

                staff = Staff(
                    staff_id=staff_id,
                    full_name_kanji=str(name) if pd.notna(name) else '',
                    full_name_kana=str(kana) if pd.notna(kana) else '',
                    monthly_salary=monthly_salary,
                    is_active=status != '退社' if pd.notna(status) else True
                )

                db.add(staff)
                db.commit()  # Commit individually
                imported += 1

            except Exception as e:
                db.rollback()
                errors += 1
                if errors < 10:
                    print(f"  ✗ Error en fila {idx}: {e}")
        print(f"✓ Importados {imported} empleados スタッフ")
        if skipped > 0:
            print(f"  ⚠ {skipped} duplicados omitidos")
        if errors > 0:
            print(f"  ⚠ {errors} errores encontrados\n")
        return imported

    except Exception as e:
        db.rollback()
        print(f"✗ Error importando スタッフ: {e}\n")
        return 0


def main():
    """Main import function"""
    db = SessionLocal()

    try:
        print("\n" + "=" * 50)
        print("INICIANDO IMPORTACIÓN DE DATOS")
        print("=" * 50 + "\n")

        # Import factories
        factories_count = import_factories(db)

        # Import employees
        haken_count = import_haken_employees(db)
        ukeoi_count = import_ukeoi_employees(db)
        staff_count = import_staff_employees(db)

        total_employees = haken_count + ukeoi_count + staff_count

        # Summary
        print("=" * 50)
        print("RESUMEN DE IMPORTACIÓN")
        print("=" * 50)
        print(f"Fábricas:        {factories_count:4d}")
        print(f"派遣社員:        {haken_count:4d}")
        print(f"請負社員:        {ukeoi_count:4d}")
        print(f"スタッフ:        {staff_count:4d}")
        print(f"{'─' * 50}")
        print(f"TOTAL Empleados: {total_employees:4d}")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Error general: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
