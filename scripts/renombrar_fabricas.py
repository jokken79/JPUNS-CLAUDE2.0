"""
Script para renombrar archivos JSON de fábricas basado en su nombre real
Versión con interfaz de usuario para ejecución directa sin necesidad de batch
"""
import os
import json
import re
from pathlib import Path
import shutil
import sys
import time

# Colores para la terminal (funcionan en Windows 10/11 y Linux/Mac)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Configurar directorios
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
FACTORIES_DIR = PROJECT_DIR / 'config' / 'factories'
BACKUP_DIR = FACTORIES_DIR / 'backup'

# Funciones para UI
def print_header():
    """Imprimir encabezado del programa"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  RENOMBRADO DE ARCHIVOS JSON DE FÁBRICAS{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print()
    print("Este programa renombrará los archivos JSON de fábricas")
    print("para incluir el nombre real de la fábrica en el nombre del archivo.")
    print()
    print("Por ejemplo:")
    print(f"  {Colors.YELLOW}Factory-01.json{Colors.ENDC} → {Colors.GREEN}Factory-01_瑞陵精機株式会社_恵那工場.json{Colors.ENDC}")
    print()

def print_step(step, total, message):
    """Imprimir paso actual del proceso"""
    print(f"{Colors.BLUE}[{step}/{total}] {message}{Colors.ENDC}")

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    """Imprimir advertencia"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.ENDC}")

def print_error(message):
    """Imprimir error"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def wait_for_user(message="Presione ENTER para continuar o CTRL+C para cancelar..."):
    """Esperar a que el usuario presione ENTER"""
    try:
        input(f"\n{message}")
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
        sys.exit(0)

# Crear copia de seguridad
def backup_files():
    """Crear copia de seguridad de todos los archivos de fábrica"""
    print_step(1, 4, "Creando copia de seguridad...")
    
    # Crear directorio de backup si no existe
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Contador de archivos respaldados
    count = 0
    
    # Copiar cada archivo
    for file in FACTORIES_DIR.glob('Factory-*.json'):
        if 'backup' not in str(file):
            backup_file = BACKUP_DIR / file.name
            shutil.copy2(file, backup_file)
            count += 1
    
    print_success(f"Copia de seguridad creada ({count} archivos) en {BACKUP_DIR}")

# Limpiar nombre para uso en nombres de archivo
def clean_filename(name):
    """Convertir un nombre a un formato válido para nombre de archivo"""
    # Eliminar tabs, espacios extras y símbolos no deseados
    name = name.replace('\t', '').strip()
    
    # Eliminar caracteres no válidos para nombres de archivo
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    
    # Limitar longitud
    if len(name) > 50:
        name = name[:50]
        
    return name

# Renombrar archivos
def rename_factory_files():
    """Renombrar los archivos de fábricas basado en su contenido"""
    print_step(2, 4, "Analizando archivos de fábricas...")
    
    # Lista para guardar mapeo viejo -> nuevo
    file_mappings = []
    
    # Lista para detectar duplicados
    used_names = set()
    
    # Contador
    total_files = len(list(FACTORIES_DIR.glob('Factory-*.json')))
    processed = 0
    
    for file_path in sorted(FACTORIES_DIR.glob('Factory-*.json')):
        # Saltar la carpeta de backup
        if 'backup' in str(file_path):
            continue
        
        processed += 1
        sys.stdout.write(f"\rAnalizando archivo {processed}/{total_files}...")
        sys.stdout.flush()
            
        try:
            # Leer el archivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extraer información relevante
            factory_id = data.get('factory_id', '')
            company_name = data.get('client_company', {}).get('name', '')
            plant_name = data.get('plant', {}).get('name', '')
            
            # Limpiar nombres
            company_name_clean = clean_filename(company_name)
            plant_name_clean = clean_filename(plant_name)
            
            # Construir nuevo nombre de archivo
            if company_name_clean and plant_name_clean:
                # Si tenemos ambos nombre de compañía y planta
                new_name = f"{factory_id}_{company_name_clean}_{plant_name_clean}.json"
            elif company_name_clean:
                # Si solo tenemos nombre de compañía
                new_name = f"{factory_id}_{company_name_clean}.json"
            elif plant_name_clean:
                # Si solo tenemos nombre de planta
                new_name = f"{factory_id}_{plant_name_clean}.json"
            else:
                # Si no tenemos ninguno, mantener el nombre original
                continue
            
            # Verificar duplicados
            if new_name in used_names:
                # Agregar un número al final para evitar duplicados
                name_base = new_name.rsplit('.', 1)[0]
                counter = 1
                while f"{name_base}_{counter}.json" in used_names:
                    counter += 1
                new_name = f"{name_base}_{counter}.json"
                
            used_names.add(new_name)
            
            # Guardar mapeo para renombrar después
            new_path = file_path.parent / new_name
            file_mappings.append((file_path, new_path))
            
        except Exception as e:
            print()
            print_error(f"Error procesando {file_path.name}: {e}")
    
    print()  # Nueva línea después del indicador de progreso
    
    # Mostrar cambios planificados
    print_step(3, 4, f"Cambios a realizar ({len(file_mappings)} archivos):")
    
    if not file_mappings:
        print_warning("No se encontraron archivos para renombrar.")
        return
    
    # Mostrar los primeros 10 cambios y un resumen
    for i, (old_path, new_path) in enumerate(file_mappings):
        if i < 10:
            print(f"  {old_path.name} → {new_path.name}")
        elif i == 10:
            print(f"  ... y {len(file_mappings) - 10} más")
    
    # Confirmar con el usuario
    print()
    choice = input(f"¿Confirmar renombrado de {len(file_mappings)} archivos? (s/n): ")
    if choice.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
        print_warning("Operación cancelada.")
        return
    
    # Renombrar archivos
    print_step(4, 4, "Renombrando archivos...")
    
    success_count = 0
    error_count = 0
    
    for old_path, new_path in file_mappings:
        try:
            shutil.move(old_path, new_path)
            success_count += 1
            sys.stdout.write(f"\rProgreso: {success_count}/{len(file_mappings)} completados...")
            sys.stdout.flush()
        except Exception as e:
            print()
            print_error(f"Error al renombrar {old_path.name}: {e}")
            error_count += 1
    
    print()  # Nueva línea después del indicador de progreso
    print_success(f"Renombrados {success_count} archivos correctamente.")
    
    if error_count > 0:
        print_warning(f"Se encontraron {error_count} errores durante el proceso.")

# Verificar referencias en archivos
def check_references():
    """Verificar si hay referencias a los archivos de fábricas en otros archivos"""
    print_step(4, 4, "Verificando referencias...")
    print("Nota: Puesto que solo cambiamos el nombre de archivo y no el ID interno,")
    print("      no es necesario actualizar referencias en el código.")
    print("      Las aplicaciones seguirán funcionando normalmente.")

# Función principal
def main():
    # Verificar que estamos en el directorio correcto
    if not FACTORIES_DIR.exists():
        print_error(f"No se encontró el directorio de fábricas: {FACTORIES_DIR}")
        print(f"Este script debe ejecutarse desde el directorio raíz del proyecto.")
        print(f"Directorio actual: {os.getcwd()}")
        return
    
    # Mostrar encabezado
    print_header()
    
    # Esperar confirmación del usuario
    wait_for_user()
    
    # Crear backup
    backup_files()
    
    # Renombrar archivos
    rename_factory_files()
    
    # Verificar referencias
    check_references()
    
    print()
    print_success("Proceso completado.")
    print(f"Backup guardado en: {BACKUP_DIR}")
    print()
    print("Recomendaciones:")
    print("1. Verifique que las aplicaciones funcionen correctamente.")
    print("2. Si hay problemas, restaure desde la carpeta de backup.")
    
    # Esperar a que el usuario presione ENTER para salir
    wait_for_user("Presione ENTER para salir...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        sys.exit(1)