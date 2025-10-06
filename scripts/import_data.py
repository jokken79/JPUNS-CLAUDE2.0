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
from app.models.models import Factory, Employee


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

                # Parse dates
                hire_date = None
                if pd.notna(row['入社日']):
                    try:
                        hire_date = pd.to_datetime(row['入社日']).date()
                    except:
                        pass

                termination_date = None
                is_active = row['現在'] != '退社' if pd.notna(row['現在']) else True
                if pd.notna(row['退社日']):
                    try:
                        termination_date = pd.to_datetime(row['退社日']).date()
                    except:
                        pass

                zairyu_expire = None
                if pd.notna(row['ビザ期限']):
                    try:
                        zairyu_expire = pd.to_datetime(row['ビザ期限']).date()
                    except:
                        pass

                dob = None
                if pd.notna(row['生年月日']):
                    try:
                        dob = pd.to_datetime(row['生年月日']).date()
                    except:
                        pass

                # Get jikyu (hourly wage)
                jikyu = 0
                if pd.notna(row['時給']):
                    try:
                        jikyu = int(float(row['時給']))
                    except:
                        jikyu = 0

                # Create employee record
                employee = Employee(
                    hakenmoto_id=hakenmoto_id,
                    factory_id=str(row['派遣先ID']) if pd.notna(row['派遣先ID']) else None,
                    full_name_kanji=str(row['氏名']) if pd.notna(row['氏名']) else '',
                    full_name_kana=str(row['カナ']) if pd.notna(row['カナ']) else '',
                    date_of_birth=dob,
                    gender=str(row['性別']) if pd.notna(row['性別']) else None,
                    nationality=str(row['国籍']) if pd.notna(row['国籍']) else None,
                    zairyu_expire_date=zairyu_expire,
                    address=str(row['住所']) if pd.notna(row['住所']) else None,
                    phone=None,  # Not in this sheet
                    email=None,  # Not in this sheet
                    hire_date=hire_date,
                    jikyu=jikyu,
                    contract_type='派遣',
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

        for idx, row in df.iterrows():
            try:
                # Get column by index since names might be problematic
                status = row.iloc[0] if len(row) > 0 else None
                shain_no = row.iloc[1] if len(row) > 1 else None

                # Skip if no employee number
                if pd.isna(shain_no):
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

                employee = Employee(
                    hakenmoto_id=int(shain_no) + 100000,  # Add offset to avoid collision with haken
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

                db.add(employee)
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

        for idx, row in df.iterrows():
            try:
                # Get by index
                status = row.iloc[0] if len(row) > 0 else None
                shain_no = row.iloc[1] if len(row) > 1 else None

                if pd.isna(shain_no):
                    continue

                name = row.iloc[2] if len(row) > 2 else ''
                kana = row.iloc[3] if len(row) > 3 else ''

                # Jikyu or monthly salary
                jikyu = 0
                if len(row) > 7 and pd.notna(row.iloc[7]):
                    try:
                        jikyu = int(float(row.iloc[7]))
                    except:
                        pass

                employee = Employee(
                    hakenmoto_id=int(shain_no) + 200000,  # Add offset
                    full_name_kanji=str(name) if pd.notna(name) else '',
                    full_name_kana=str(kana) if pd.notna(kana) else '',
                    jikyu=jikyu,
                    contract_type='スタッフ',
                    is_active=status != '退社' if pd.notna(status) else True
                )

                db.add(employee)
                db.commit()  # Commit individually
                imported += 1

            except Exception as e:
                db.rollback()
                errors += 1
                if errors < 10:
                    print(f"  ✗ Error en fila {idx}: {e}")
        print(f"✓ Importados {imported} empleados スタッフ")
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
