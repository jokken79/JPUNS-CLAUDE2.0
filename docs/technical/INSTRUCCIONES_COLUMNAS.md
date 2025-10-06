# Instrucciones para Ocultar/Mostrar Columnas en Excel

## 📋 Columnas Completas del Sistema

Tu Excel tiene estas columnas (incluyendo las que estaban ocultas):

```
現在, 社員№, 派遣先ID, 派遣先, 配属先, 配属ライン, 仕事内容,
氏名, カナ, 性別, 国籍, 生年月日, 年齢, 時給, 時給改定,
請求単価, 請求改定, 差額利益, 標準報酬, 健康保険, 介護保険,
厚生年金, ビザ期限, ｱﾗｰﾄ(ﾋﾞｻﾞ更新), ビザ種類, 〒, 住所, ｱﾊﾟｰﾄ,
入居, 入社日, 退社日, 退去, 社保加入, 入社依頼, 備考, 現入社,
免許種類, 免許期限, 通勤方法, 任意保険期限, 日本語検定,
キャリアアップ5年目
```

## 🔧 Cómo Ocultar/Mostrar Columnas en Excel

### Método 1: Ocultar columnas individuales
1. Selecciona la(s) columna(s) que quieres ocultar (click en la letra de la columna)
2. Click derecho → "Ocultar"

### Método 2: Mostrar columnas ocultas
1. Selecciona las columnas antes y después de las ocultas
2. Click derecho → "Mostrar"

### Método 3: Mostrar todas las columnas
1. Selecciona todas las columnas (Ctrl + A)
2. Click derecho en cualquier encabezado de columna → "Mostrar"

## ✅ Columnas Requeridas para Importación

**Columna obligatoria:**
- `社員№` - Si existe, actualiza; si no, crea nuevo

**Columnas importantes:**
- `現在` - Para determinar si está activo (在籍中) o retirado (退社)
- `派遣先` - **Nombre de la fábrica** (el sistema buscará la fábrica por nombre)
- `派遣先ID` - **ID que la fábrica le otorga al empleado** (NO el ID de la fábrica)
- `氏名` - Nombre del empleado
- `入社日` - Fecha de ingreso

**IMPORTANTE:**
- `派遣先ID` ≠ ID de la fábrica
- `派遣先ID` = ID del empleado en la fábrica (ejemplo: "F01-001", "PMI-123", etc.)
- `派遣先` = Nombre de la fábrica (ejemplo: "ピーエムアイ有限会社", "瑞陵精機株式会社", etc.)

**Todas las demás columnas son opcionales** - Si están vacías, se importarán como NULL.

## 📝 Nota sobre las Macros

- El sistema **ignora las macros** de tu Excel
- Solo lee los **valores** de las celdas
- Puedes importar directamente tu Excel con macros
- Las columnas calculadas (como 年齢) se pueden dejar vacías si se calculan automáticamente

## 🔄 Para Importar

1. Asegúrate que los **nombres de las columnas** coincidan exactamente
2. Puedes tener columnas ocultas - el sistema las leerá igual
3. Ve a **"データインポート"** en el menú
4. Sube tu archivo Excel (.xlsx o .xls)
5. El sistema procesará todas las columnas automáticamente
