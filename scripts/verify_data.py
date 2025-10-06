"""Verify imported data"""
import sys
sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from app.models.models import Factory, Employee

db = SessionLocal()

print("=" * 60)
print("VERIFICACIÓN DE DATOS IMPORTADOS")
print("=" * 60)

# Factories
factory_count = db.query(Factory).count()
print(f"\n✓ Fábricas: {factory_count}")

# Employees by type
haken_count = db.query(Employee).filter(Employee.contract_type == '派遣').count()
ukeoi_count = db.query(Employee).filter(Employee.contract_type == '請負').count()
staff_count = db.query(Employee).filter(Employee.contract_type == 'スタッフ').count()

print(f"\n✓ Empleados por tipo:")
print(f"  派遣社員 (Dispatch):  {haken_count:4d}")
print(f"  請負社員 (Contract):  {ukeoi_count:4d}")
print(f"  スタッフ (Staff):     {staff_count:4d}")

# Active vs Inactive
active_count = db.query(Employee).filter(Employee.is_active == True).count()
inactive_count = db.query(Employee).filter(Employee.is_active == False).count()

print(f"\n✓ Estado de empleados:")
print(f"  Activos:    {active_count:4d}")
print(f"  Inactivos:  {inactive_count:4d}")

total_employees = db.query(Employee).count()
print(f"\n{'=' * 60}")
print(f"TOTAL EMPLEADOS: {total_employees}")
print(f"{'=' * 60}")

# Sample employees
print(f"\n📋 Muestra de empleados (primeros 10):")
print(f"{'-' * 60}")
employees = db.query(Employee).limit(10).all()
for e in employees:
    status = "✓ ACTIVO" if e.is_active else "✗ INACTIVO"
    print(f"{e.hakenmoto_id:7d} | {e.full_name_kanji:25s} | {e.contract_type:8s} | ¥{e.jikyu:5d}/h | {status}")

db.close()
