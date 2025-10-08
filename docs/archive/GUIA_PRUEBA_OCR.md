# Guía de Prueba - Sistema OCR Mejorado

## 🎯 URL de Prueba
```
http://localhost:3000/templates/rirekisho.html
```

---

## ✅ Lo que DEBERÍAS VER ahora

### Antes de Subir Archivo:
```
┌─────────────────────────────────┐
│   在留カード                    │
│                                 │
│  [📄 Área de carga]            │
│   クリックしてアップロード      │
└─────────────────────────────────┘
```

### PASO 1 - Inmediatamente después de seleccionar archivo:
```
┌─────────────────────────────────┐
│ [Imagen preview]                │
├─────────────────────────────────┤
│ 📄 画像を読み込んでいます...   │
├─────────────────────────────────┤
│ ▓▓▓░░░░░░░░░░░ [barra animada] │
├─────────────────────────────────┤
│ ステップ 1/3: アップロード中...│
└─────────────────────────────────┘
```

### PASO 2 - Enviando al servidor:
```
┌─────────────────────────────────┐
│ [Imagen preview]                │
├─────────────────────────────────┤
│ 🔍 OCR処理中...               │
│ (テキストを抽出しています)      │
├─────────────────────────────────┤
│ ▓▓▓░░░░░░░░░░░ [barra animada] │
├─────────────────────────────────┤
│ ステップ 2/3: サーバーで処理中...│
└─────────────────────────────────┘
```

### PASO 3 - Procesando datos:
```
┌─────────────────────────────────┐
│ [Imagen preview]                │
├─────────────────────────────────┤
│ 📝 データを解析しています...   │
├─────────────────────────────────┤
│ ▓▓▓░░░░░░░░░░░ [barra animada] │
├─────────────────────────────────┤
│ ステップ 3/3: データ解析中...  │
└─────────────────────────────────┘
```

### ÉXITO - Completado:
```
┌─────────────────────────────────┐
│ [Imagen preview]                │
├─────────────────────────────────┤
│ ✅ 処理完了！                  │
│ データを入力しました            │
└─────────────────────────────────┘

Y el formulario se auto-rellena con:
✓ Nombre
✓ Fecha de nacimiento
✓ Edad (calculada)
✓ Género
✓ Nacionalidad
✓ Dirección
✓ Foto del rostro
```

---

## ❌ ERRORES que podrías ver

### Error 1: Archivo muy grande (>10MB)
```
┌─────────────────────────────────────┐
│ ❌ エラーが発生しました           │
│                                     │
│ ファイルサイズが大きすぎます。     │
│ 10MB以下のファイルを選択してください│
│ (File too large, max 10MB)          │
└─────────────────────────────────────┘
```

### Error 2: Tipo de archivo inválido
```
┌─────────────────────────────────────┐
│ ❌ エラーが発生しました           │
│                                     │
│ 無効なファイル形式です。           │
│ JPG、PNG、またはPDFファイルを      │
│ 選択してください。                 │
│ (Invalid file type)                 │
└─────────────────────────────────────┘
```

### Error 3: Backend apagado
```
┌─────────────────────────────────────┐
│ ❌ エラーが発生しました           │
│                                     │
│ サーバーに接続できません。         │
│ バックエンドが起動しているか       │
│ 確認してください。                 │
│ (Cannot connect to server)          │
└─────────────────────────────────────┘
```

### Error 4: Timeout (60 segundos)
```
┌─────────────────────────────────────┐
│ ❌ エラーが発生しました           │
│                                     │
│ 処理がタイムアウトしました。       │
│ サーバーが応答していません。       │
│ (Request timeout)                   │
└─────────────────────────────────────┘
```

### Error 5: OCR falló (imagen borrosa)
```
┌─────────────────────────────────────┐
│ ❌ エラーが発生しました           │
│                                     │
│ サーバーエラーが発生しました。     │
│ 画像が不鮮明である可能性があります。│
│ (Server error - Image may be unclear)│
└─────────────────────────────────────┘
```

---

## 🧪 CASOS DE PRUEBA

### ✅ Prueba 1: Archivo Válido
**Acción:** Sube una imagen JPG de 在留カード clara (< 10MB)
**Esperado:**
1. Ver Paso 1/3
2. Ver Paso 2/3
3. Ver Paso 3/3
4. Ver ✅ 処理完了！
5. Formulario auto-rellenado

### ❌ Prueba 2: Archivo Grande
**Acción:** Intenta subir archivo > 10MB
**Esperado:**
- Error INMEDIATO (antes de subir)
- Mensaje: "ファイルサイズが大きすぎます..."

### ❌ Prueba 3: Archivo Incorrecto
**Acción:** Intenta subir .docx o .txt
**Esperado:**
- Error INMEDIATO
- Mensaje: "無効なファイル形式です..."

### ❌ Prueba 4: Backend Apagado
**Acción:**
1. Detén el backend: `docker stop uns-claudejp-backend`
2. Intenta subir imagen válida
**Esperado:**
- Ver Paso 1/3
- Esperar timeout (60s)
- Mensaje: "サーバーに接続できません..."

### ✅ Prueba 5: Reintentar después de Error
**Acción:**
1. Genera un error (cualquiera)
2. Sube otra imagen
**Esperado:**
- Input se limpia automáticamente
- Puedes subir de nuevo sin problema
- Proceso inicia desde cero

---

## 🔍 DEBUGGING

### Ver Console del Navegador (F12):

#### Proceso Exitoso:
```
Sending request to backend OCR API...
✅ OCR処理成功: {name: "...", birthday: "..."}
✓ Auto-converted name to Katakana: ...
✓ Edad calculada: 25
✓ Género: 男性
✓ Nacionalidad: ベトナム
```

#### Proceso con Error:
```
❌ OCR Error: Error: サーバーに接続できません...
📋 Detalles del error:
  - Tipo de documento: zairyu
  - Nombre del archivo: IMG_123.jpg
  - Tamaño del archivo: 2543.21 KB
  - Tipo MIME: image/jpeg
  - Error completo: TypeError: Failed to fetch
```

---

## 🎨 COLORES DE ESTADO

### Azul (Procesando):
- Fondo: #DBEAFE
- Texto: #1D4ED8
- Significa: Trabajando...

### Verde (Éxito):
- Fondo: #D1FAE5
- Texto: #059669
- Significa: ¡Listo!

### Rojo (Error):
- Fondo: #FEE2E2
- Texto: #DC2626
- Significa: Algo falló

---

## 📱 COMPATIBILIDAD

✅ Chrome
✅ Edge
✅ Firefox
✅ Safari

---

## ⚙️ CONFIGURACIÓN ACTUAL

- **Timeout:** 60 segundos
- **Tamaño máximo:** 10MB
- **Formatos:** JPG, PNG, PDF
- **Servidor:** http://localhost:8000
- **Endpoint:** /api/candidates/ocr/process

---

## 🆘 SI AÚN VES EL MENSAJE ANTIGUO

1. **Hard Refresh:**
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **Limpiar Caché:**
   - Chrome: F12 → Network tab → Disable cache (checkbox)
   - Luego recargar (F5)

3. **Modo Incógnito:**
   - Abre en ventana incógnita
   - `Ctrl + Shift + N` (Chrome)

4. **Verificar versión del archivo:**
   ```bash
   curl http://localhost:3000/templates/rirekisho.html | grep "progress-container"
   ```
   - Debería mostrar: `progress-container` 3 veces

---

**Última Actualización:** 2025-10-07 12:38
**Estado:** ✅ Desplegado y funcionando
