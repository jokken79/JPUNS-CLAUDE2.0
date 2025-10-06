"""Create initial admin user"""
import sys
sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from app.models.models import User, UserRole
from app.services.auth_service import AuthService

db = SessionLocal()

print("=" * 80)
print("CREANDO USUARIO ADMINISTRADOR INICIAL")
print("=" * 80)

# Check if admin already exists
existing_admin = db.query(User).filter(User.username == 'admin').first()

if existing_admin:
    print("\n⚠ Usuario 'admin' ya existe")
    print(f"   Email: {existing_admin.email}")
    print(f"   Rol: {existing_admin.role.value}")
else:
    # Create admin user
    admin_user = User(
        username='admin',
        email='admin@uns-kikaku.com',
        password_hash=AuthService.get_password_hash('admin123'),
        role=UserRole.SUPER_ADMIN,
        full_name='Administrador del Sistema',
        is_active=True
    )

    db.add(admin_user)
    db.commit()

    print("\n✓ Usuario administrador creado exitosamente!")
    print(f"\n   Username: admin")
    print(f"   Password: admin123")
    print(f"   Email:    admin@uns-kikaku.com")
    print(f"   Rol:      SUPER_ADMIN")

# Create a test coordinator user
existing_coordinator = db.query(User).filter(User.username == 'coordinator').first()

if not existing_coordinator:
    coordinator_user = User(
        username='coordinator',
        email='coordinator@uns-kikaku.com',
        password_hash=AuthService.get_password_hash('coord123'),
        role=UserRole.COORDINATOR,
        full_name='Coordinador de Prueba',
        is_active=True
    )

    db.add(coordinator_user)
    db.commit()

    print("\n✓ Usuario coordinador creado!")
    print(f"\n   Username: coordinator")
    print(f"   Password: coord123")
    print(f"   Email:    coordinator@uns-kikaku.com")
    print(f"   Rol:      COORDINATOR")

# Summary
print("\n" + "=" * 80)
print("USUARIOS CREADOS")
print("=" * 80)

all_users = db.query(User).all()
print(f"\nTotal usuarios: {len(all_users)}\n")

for user in all_users:
    status = "✓ ACTIVO" if user.is_active else "✗ INACTIVO"
    print(f"  {user.username:15s} | {user.role.value:15s} | {user.email:30s} | {status}")

print("\n" + "=" * 80)
print("ACCESO AL SISTEMA:")
print("=" * 80)
print("\nFrontend: http://localhost:3000")
print("Backend:  http://localhost:8000")
print("API Docs: http://localhost:8000/docs")
print("\n" + "=" * 80)

db.close()
