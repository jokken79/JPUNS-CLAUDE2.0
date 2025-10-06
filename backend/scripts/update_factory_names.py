"""
Script para actualizar nombres de fábricas en la base de datos
Ejecutar: docker exec uns-claudejp-backend python /app/scripts/update_factory_names.py
"""

from app.core.database import SessionLocal
from app.models.models import Factory

# Diccionario con los nombres de las fábricas
# Formato: 'Factory-ID': 'Nombre de la fábrica'
FACTORY_NAMES = {
    'Factory-03': 'Nombre Fábrica 03',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-05': 'Nombre Fábrica 05',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-07': 'Nombre Fábrica 07',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-09': 'Nombre Fábrica 09',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-13': 'Nombre Fábrica 13',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-26': 'Nombre Fábrica 26',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-27': 'Nombre Fábrica 27',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-29': 'Nombre Fábrica 29',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-33': 'Nombre Fábrica 33',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-36': 'Nombre Fábrica 36',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-38': 'Nombre Fábrica 38',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-47': 'Nombre Fábrica 47',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-61': 'Nombre Fábrica 61',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-68': 'Nombre Fábrica 68',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-69': 'Nombre Fábrica 69',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-76': 'Nombre Fábrica 76',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-82': 'Nombre Fábrica 82',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-83': 'Nombre Fábrica 83',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-97': 'Nombre Fábrica 97',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-99': 'Nombre Fábrica 99',  # ACTUALIZAR CON NOMBRE REAL
    'Factory-101': 'Nombre Fábrica 101',  # ACTUALIZAR CON NOMBRE REAL
}


def update_factory_names():
    """Actualiza los nombres de las fábricas"""
    db = SessionLocal()

    try:
        updated_count = 0

        for factory_id, new_name in FACTORY_NAMES.items():
            factory = db.query(Factory).filter(Factory.factory_id == factory_id).first()

            if factory:
                old_name = factory.name
                factory.name = new_name
                print(f'✓ {factory_id}: "{old_name}" → "{new_name}"')
                updated_count += 1
            else:
                print(f'✗ {factory_id}: No encontrada en BD')

        db.commit()
        print(f'\n✅ Total actualizado: {updated_count} fábricas')

    except Exception as e:
        db.rollback()
        print(f'❌ Error: {str(e)}')
        raise
    finally:
        db.close()


if __name__ == '__main__':
    print('=' * 80)
    print('ACTUALIZACIÓN DE NOMBRES DE FÁBRICAS')
    print('=' * 80)
    print()

    # Confirmar antes de ejecutar
    print('Fábricas a actualizar:')
    for factory_id, name in FACTORY_NAMES.items():
        print(f'  - {factory_id} → {name}')

    print()
    response = input('¿Continuar con la actualización? (s/n): ')

    if response.lower() == 's':
        update_factory_names()
    else:
        print('Operación cancelada')
