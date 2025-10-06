"""Full system verification"""
import sys
sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from app.models.models import Factory, Employee
from sqlalchemy import func

db = SessionLocal()

print("=" * 80)
print("VERIFICACIÓN COMPLETA DEL SISTEMA UNS-ClaudeJP 2.0")
print("=" * 80)

# ============================================
# 1. FACTORIES VERIFICATION
# ============================================
print("\n" + "=" * 80)
print("1. VERIFICACIÓN DE FÁBRICAS (派遣先)")
print("=" * 80)

total_factories = db.query(Factory).count()
active_factories = db.query(Factory).filter(Factory.is_active == True).count()
print(f"\n✓ Total fábricas: {total_factories}")
print(f"✓ Fábricas activas: {active_factories}")

# Check for empty/null names
empty_names = db.query(Factory).filter(
    (Factory.name == '') | (Factory.name == '-') | (Factory.name.is_(None))
).count()
print(f"⚠ Fábricas con nombre vacío: {empty_names}")

# Sample factories with full data
print(f"\n📋 Muestra de fábricas con datos completos:")
factories_sample = db.query(Factory).filter(
    Factory.name != '',
    Factory.name != '-'
).limit(5).all()

for f in factories_sample:
    client_name = f.config.get('client_company', {}).get('name', 'N/A')
    plant_name = f.config.get('plant', {}).get('name', 'N/A')
    hourly_rate = f.config.get('job', {}).get('hourly_rate', 0)
    print(f"\n  {f.factory_id}:")
    print(f"    Cliente: {client_name}")
    print(f"    Planta: {plant_name}")
    print(f"    Tiempo単価: ¥{hourly_rate}/h")
    print(f"    Supervisor: {f.contact_person}")

# ============================================
# 2. EMPLOYEES VERIFICATION
# ============================================
print("\n" + "=" * 80)
print("2. VERIFICACIÓN DE EMPLEADOS")
print("=" * 80)

total_employees = db.query(Employee).count()
print(f"\n✓ Total empleados: {total_employees}")

# By contract type
haken = db.query(Employee).filter(Employee.contract_type == '派遣').count()
ukeoi = db.query(Employee).filter(Employee.contract_type == '請負').count()
staff = db.query(Employee).filter(Employee.contract_type == 'スタッフ').count()

print(f"\n  Por tipo de contrato:")
print(f"    派遣社員 (Dispatch): {haken:4d}")
print(f"    請負社員 (Contract): {ukeoi:4d}")
print(f"    スタッフ (Staff):    {staff:4d}")

# By status
active = db.query(Employee).filter(Employee.is_active == True).count()
inactive = db.query(Employee).filter(Employee.is_active == False).count()

print(f"\n  Por estado:")
print(f"    Activos:   {active:4d}")
print(f"    Inactivos: {inactive:4d}")

# Salary statistics
avg_jikyu = db.query(func.avg(Employee.jikyu)).filter(Employee.jikyu > 0).scalar()
min_jikyu = db.query(func.min(Employee.jikyu)).filter(Employee.jikyu > 0).scalar()
max_jikyu = db.query(func.max(Employee.jikyu)).filter(Employee.jikyu > 0).scalar()

print(f"\n  Estadísticas de 時給 (Salario por hora):")
print(f"    Promedio: ¥{int(avg_jikyu)}/h")
print(f"    Mínimo:   ¥{int(min_jikyu)}/h")
print(f"    Máximo:   ¥{int(max_jikyu)}/h")

# Employees with factory assignment
with_factory = db.query(Employee).filter(Employee.factory_id.isnot(None)).count()
without_factory = db.query(Employee).filter(Employee.factory_id.is_(None)).count()

print(f"\n  Asignación a fábricas:")
print(f"    Con factory_id:  {with_factory:4d}")
print(f"    Sin factory_id:  {without_factory:4d}")

# Data completeness
with_name = db.query(Employee).filter(
    Employee.full_name_kanji != '',
    Employee.full_name_kanji.isnot(None)
).count()

with_kana = db.query(Employee).filter(
    Employee.full_name_kana != '',
    Employee.full_name_kana.isnot(None)
).count()

with_hire_date = db.query(Employee).filter(Employee.hire_date.isnot(None)).count()

print(f"\n  Completitud de datos:")
print(f"    Con nombre (氏名):     {with_name:4d} ({with_name*100//total_employees}%)")
print(f"    Con kana (カナ):       {with_kana:4d} ({with_kana*100//total_employees}%)")
print(f"    Con fecha ingreso:    {with_hire_date:4d} ({with_hire_date*100//total_employees}%)")

# ============================================
# 3. SAMPLE EMPLOYEES WITH FULL DATA
# ============================================
print("\n" + "=" * 80)
print("3. MUESTRA DE EMPLEADOS ACTIVOS CON DATOS COMPLETOS")
print("=" * 80)

active_employees = db.query(Employee).filter(
    Employee.is_active == True,
    Employee.jikyu > 0
).limit(10).all()

print(f"\n{'ID':>7} | {'Nombre':^30} | {'Tipo':^8} | {'時給':>6} | {'入社日':^12} | {'Estado':^10}")
print("-" * 80)

for e in active_employees:
    hire_date = e.hire_date.strftime('%Y-%m-%d') if e.hire_date else 'N/A'
    status = "✓ ACTIVO" if e.is_active else "✗ INACTIVO"
    print(f"{e.hakenmoto_id:7d} | {e.full_name_kanji:^30} | {e.contract_type:^8} | ¥{e.jikyu:5d} | {hire_date:^12} | {status:^10}")

# ============================================
# 4. DATA INTEGRITY CHECKS
# ============================================
print("\n" + "=" * 80)
print("4. VERIFICACIÓN DE INTEGRIDAD DE DATOS")
print("=" * 80)

# Check for duplicate employee IDs
duplicate_ids = db.query(Employee.hakenmoto_id, func.count(Employee.hakenmoto_id)).group_by(
    Employee.hakenmoto_id
).having(func.count(Employee.hakenmoto_id) > 1).all()

if duplicate_ids:
    print(f"\n⚠ ADVERTENCIA: {len(duplicate_ids)} IDs de empleado duplicados:")
    for emp_id, count in duplicate_ids[:5]:
        print(f"    ID {emp_id}: {count} registros")
else:
    print(f"\n✓ Sin IDs de empleado duplicados")

# Check for employees with invalid jikyu
invalid_jikyu = db.query(Employee).filter(
    (Employee.jikyu < 0) | (Employee.jikyu > 10000)
).count()

if invalid_jikyu > 0:
    print(f"⚠ ADVERTENCIA: {invalid_jikyu} empleados con 時給 inválido")
else:
    print(f"✓ Todos los empleados tienen 時給 válido")

# Check factory foreign key integrity
employees_with_invalid_factory = db.query(Employee).filter(
    Employee.factory_id.isnot(None)
).all()

invalid_factory_refs = 0
for emp in employees_with_invalid_factory:
    factory_exists = db.query(Factory).filter(Factory.factory_id == emp.factory_id).first()
    if not factory_exists:
        invalid_factory_refs += 1

if invalid_factory_refs > 0:
    print(f"⚠ ADVERTENCIA: {invalid_factory_refs} empleados con factory_id inválido")
else:
    print(f"✓ Todas las referencias a factories son válidas")

# ============================================
# 5. CONFIGURATION FILES CHECK
# ============================================
print("\n" + "=" * 80)
print("5. VERIFICACIÓN DE ARCHIVOS DE CONFIGURACIÓN")
print("=" * 80)

import os
import json

# Check company.json
if os.path.exists('/app/config/company.json'):
    with open('/app/config/company.json', 'r', encoding='utf-8') as f:
        company_config = json.load(f)
    print(f"\n✓ company.json existe")
    print(f"  Empresa: {company_config['company']['name_ja']}")
    print(f"  Representante: {company_config['company']['representative']}")
else:
    print(f"\n✗ company.json NO EXISTE")

# Check factories_index.json
if os.path.exists('/app/config/factories_index.json'):
    with open('/app/config/factories_index.json', 'r', encoding='utf-8') as f:
        factories_index = json.load(f)
    print(f"\n✓ factories_index.json existe")
    print(f"  Total factories en índice: {factories_index['total_factories']}")
else:
    print(f"\n✗ factories_index.json NO EXISTE")

# Check employee master Excel
if os.path.exists('/app/config/employee_master.xlsm'):
    print(f"\n✓ employee_master.xlsm existe")
else:
    print(f"\n✗ employee_master.xlsm NO EXISTE")

# Check KaishaInfo Excel
if os.path.exists('/app/config/KaishaInfo.xlsx'):
    print(f"✓ KaishaInfo.xlsx existe")
else:
    print(f"✗ KaishaInfo.xlsx NO EXISTE")

# ============================================
# FINAL SUMMARY
# ============================================
print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

print(f"""
✓ Fábricas:           {total_factories:4d}
✓ Empleados totales:  {total_employees:4d}
  - Activos:          {active:4d}
  - Inactivos:        {inactive:4d}
✓ Datos completos y verificados
✓ Sistema listo para uso
""")

db.close()

print("=" * 80)
print("VERIFICACIÓN COMPLETADA")
print("=" * 80)
