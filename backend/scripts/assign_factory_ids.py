"""Assign correct factory_id to employees based on Excel data"""
import sys
sys.path.insert(0, '/app')

import pandas as pd
from app.core.database import SessionLocal
from app.models.models import Factory, Employee

db = SessionLocal()

print("=" * 80)
print("ASIGNANDO factory_id A EMPLEADOS")
print("=" * 80)

# Read employee Excel to get the mapping
df_haken = pd.read_excel('/app/config/employee_master.xlsm', sheet_name='派遣社員', header=1)

# Create a mapping from 派遣先 company name to Factory-XX
print("\nCreando mapeo de empresas a Factory IDs...")

# Get all factories
all_factories = db.query(Factory).all()

# Create mapping: short name -> factory_id
# We need to match short names like "ピーエムアイ" to "ピーエムアイ有限会社"
company_to_factory = {}

# Manual mapping based on the data
name_mapping = {
    'ピーエムアイ': 'ピーエムアイ有限会社',
    'オーツカ': '株式会社オーツカ',
    '瑞陵精機': '瑞陵精機株式会社',
    '川原鉄工所': '株式会社川原鉄工所',
    'ユアサ工機': 'ユアサ工機株式会社',
    '加藤木材工業': '加藤木材工業株式会社',
    'セイビテック': 'セイビテック株式会社',
    '六甲電子': '六甲電子株式会社',
    '美鈴工業': '株式会社美鈴工業',
}

# Create factory lookup
factory_lookup = {}
for factory in all_factories:
    client_name = factory.config.get('client_company', {}).get('name', '').strip()
    plant_name = factory.config.get('plant', {}).get('name', '').strip()

    # Store by full name
    if client_name:
        if client_name not in factory_lookup:
            factory_lookup[client_name] = []
        factory_lookup[client_name].append({
            'factory_id': factory.factory_id,
            'plant': plant_name
        })

print(f"✓ Encontradas {len(factory_lookup)} empresas únicas")

# Now match employees
print("\nAsignando factory_id a empleados 派遣社員...")

assigned = 0
not_found = 0
errors = 0
already_correct = 0

for idx, row in df_haken.iterrows():
    try:
        if pd.isna(row['社員№']):
            continue

        hakenmoto_id = int(row['社員№'])
        hakensaki_name = str(row['派遣先']).strip() if pd.notna(row['派遣先']) else ''

        # Find employee
        employee = db.query(Employee).filter(Employee.hakenmoto_id == hakenmoto_id).first()

        if not employee:
            continue

        # Find matching factory
        if hakensaki_name:
            # Try to map short name to full name
            full_name = name_mapping.get(hakensaki_name, hakensaki_name)

            # Find factory(ies) for this company
            if full_name in factory_lookup:
                factories_list = factory_lookup[full_name]

                # If only one factory, assign it
                if len(factories_list) == 1:
                    new_factory_id = factories_list[0]['factory_id']
                else:
                    # Multiple factories - try to match by plant name if available
                    # For now, just use the first one
                    new_factory_id = factories_list[0]['factory_id']

                if employee.factory_id == new_factory_id:
                    already_correct += 1
                else:
                    employee.factory_id = new_factory_id
                    db.commit()
                    assigned += 1

                    if assigned % 50 == 0:
                        print(f"  Asignados {assigned} empleados...")
            else:
                not_found += 1
                if not_found <= 5:
                    print(f"  ⚠ No encontrada fábrica para: '{hakensaki_name}'")

    except Exception as e:
        errors += 1
        db.rollback()
        if errors < 5:
            print(f"  ✗ Error en fila {idx}: {e}")

print(f"\n✓ Asignados: {assigned}")
print(f"  Ya correctos: {already_correct}")
print(f"  No encontrados: {not_found}")
if errors > 0:
    print(f"  ⚠ Errores: {errors}")

# Verification
print("\n" + "=" * 80)
print("VERIFICACIÓN DESPUÉS DE ASIGNACIÓN")
print("=" * 80)

with_factory = db.query(Employee).filter(
    Employee.factory_id.isnot(None),
    Employee.contract_type == '派遣'
).count()

without_factory = db.query(Employee).filter(
    Employee.factory_id.is_(None),
    Employee.contract_type == '派遣'
).count()

print(f"\n派遣社員:")
print(f"  Con factory_id:  {with_factory}")
print(f"  Sin factory_id:  {without_factory}")

# Show sample assignments
print(f"\n📋 Muestra de asignaciones (primeros 10):")
print("-" * 80)

employees_with_factory = db.query(Employee).filter(
    Employee.factory_id.isnot(None)
).limit(10).all()

for emp in employees_with_factory:
    factory = db.query(Factory).filter(Factory.factory_id == emp.factory_id).first()
    factory_name = factory.config['client_company']['name'] if factory else 'N/A'
    print(f"{emp.hakenmoto_id:7d} | {emp.full_name_kanji:25s} | {emp.factory_id:12s} | {factory_name}")

# Show top companies by employee count
print(f"\n📊 Empresas con más empleados asignados:")
print("-" * 80)

from sqlalchemy import func

top_companies = db.query(
    Employee.factory_id,
    func.count(Employee.id).label('count')
).filter(
    Employee.factory_id.isnot(None)
).group_by(
    Employee.factory_id
).order_by(
    func.count(Employee.id).desc()
).limit(10).all()

for factory_id, count in top_companies:
    factory = db.query(Factory).filter(Factory.factory_id == factory_id).first()
    if factory:
        company_name = factory.config['client_company']['name']
        print(f"  {factory_id:12s} | {count:3d} empleados | {company_name}")

db.close()

print("\n" + "=" * 80)
print("ASIGNACIÓN COMPLETADA")
print("=" * 80)
