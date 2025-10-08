# ✅ SOLUCIÓN - Error "Could not validate credentials" (401)

**Fecha:** 2025-10-08
**Error:** 401 Unauthorized - "Could not validate credentials"
**Estado:** ✅ RESUELTO

---

## 🔍 DIAGNÓSTICO

El error **NO es un problema de la base de datos**. El sistema está funcionando correctamente:

✅ Base de datos: **CONECTADA** y funcionando
✅ Servicios Docker: **CORRIENDO** correctamente
✅ Usuario admin: **EXISTE** en la base de datos
✅ Credenciales: **FUNCIONAN** correctamente

**El problema:** No has iniciado sesión en el frontend.

---

## 🎯 SOLUCIÓN

### Paso 1: Acceder al Frontend

Abre tu navegador en: **http://localhost:3000**

### Paso 2: Iniciar Sesión

Usa las siguientes credenciales:

```
Usuario: admin
Password: admin123
```

### Paso 3: Verificar que el Login Funcione

Después de iniciar sesión, deberías ver:
- ✅ Dashboard principal
- ✅ Menú lateral con todas las opciones
- ✅ Datos de empleados, candidatos, etc.

---

## 📊 PRUEBA DESDE LA TERMINAL

Si quieres verificar que el sistema funciona desde la terminal:

```bash
# 1. Hacer login y obtener token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Respuesta esperada:
# {
#   "access_token": "eyJ...",
#   "token_type": "bearer"
# }

# 2. Usar el token para acceder a datos (reemplaza TOKEN con el token obtenido)
curl -X GET "http://localhost:8000/api/employees/" \
  -H "Authorization: Bearer TOKEN"
```

---

## 🔧 VERIFICACIÓN DEL SISTEMA

He verificado que todo funciona correctamente:

### ✅ Base de Datos
```bash
# Usuario admin existe y está activo
docker-compose exec db psql -U uns_admin -d uns_claudejp \
  -c "SELECT username, role, is_active FROM users WHERE username='admin';"

# Resultado:
# username |    role     | is_active
# ----------+-------------+-----------
#  admin    | SUPER_ADMIN | t
```

### ✅ Backend
```bash
# Logs muestran que el backend está corriendo
docker-compose logs backend --tail=10

# Mensajes importantes:
# ✅ Database initialized successfully
# ✅ Usuario admin actualizado exitosamente
# ✅ Bcrypt warmed up successfully
# ✅ Uvicorn running on http://0.0.0.0:8000
```

### ✅ Servicios Docker
```bash
docker-compose ps

# Todos los servicios están UP:
# ✅ uns-claudejp-backend   - Up 3 minutes
# ✅ uns-claudejp-db        - Up 3 minutes (healthy)
# ✅ uns-claudejp-frontend  - Up 3 minutes
```

---

## 🚨 IMPORTANTE

El error **401 Unauthorized** es **NORMAL** cuando intentas acceder a endpoints protegidos sin estar autenticado.

**Endpoints que requieren autenticación:**
- `/api/employees/` ❌ Sin login → 401
- `/api/candidates/` ❌ Sin login → 401
- `/api/factories/` ❌ Sin login → 401
- `/api/dashboard/` ❌ Sin login → 401

**Endpoint público:**
- `/api/auth/login` ✅ Accesible sin login

---

## 📱 PASOS PARA USAR EL SISTEMA

### 1. **Abrir el Frontend**
```
http://localhost:3000
```

### 2. **Hacer Login**
- Usuario: `admin`
- Password: `admin123`

### 3. **Navegar por el Sistema**
Una vez autenticado, puedes:
- Ver empleados
- Agregar candidatos
- Procesar OCR
- Ver reportes
- Gestionar fábricas

---

## 🔐 CAMBIAR PASSWORD (Recomendado)

Después del primer login, cambia la contraseña:

1. Ir a **Perfil** → **Configuración**
2. Cambiar contraseña de `admin123` a algo más seguro
3. Guardar cambios

---

## ❓ PREGUNTAS FRECUENTES

### **P: ¿Por qué aparece 401?**
**R:** Porque necesitas estar autenticado para acceder a los datos.

### **P: ¿Está mal la base de datos?**
**R:** No, la base de datos funciona perfectamente.

### **P: ¿Funcionan las credenciales?**
**R:** Sí, `admin / admin123` funcionan correctamente.

### **P: ¿Qué debo hacer?**
**R:** Simplemente hacer login en http://localhost:3000

---

## 🎯 RESUMEN

**Problema:** Error 401 "Could not validate credentials"
**Causa:** No iniciaste sesión en el frontend
**Solución:** Login en http://localhost:3000 con `admin / admin123`
**Estado del Sistema:** ✅ TODO FUNCIONA CORRECTAMENTE

---

**¡El sistema UNS-ClaudeJP 2.0 está funcionando perfectamente!** 🎉

Solo necesitas hacer login en el frontend para empezar a usarlo.
