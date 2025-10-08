# UNS-ClaudeJP 2.0

UNS企画用の総合人材管理システム - バージョン2.0

---

## 📋 目次

1. [システム概要](#システム概要)
2. [動作環境](#動作環境)
3. [インストール手順（Windows）](#インストール手順windows)
4. [初期設定](#初期設定)
5. [使い方](#使い方)
6. [トラブルシューティング](#トラブルシューティング)

---

## システム概要

### 主な機能

#### 📋 採用管理モジュール
- ✅ 履歴書の自動OCR処理（日本語対応）
- ✅ 在留カード・免許証の読み取り（システムハイブリッド：Gemini + Vision + Tesseract）
- ✅ 候補者ID自動生成（UNS-1000~）
- ✅ 入社届の自動作成
- ✅ 書類管理（PDF/JPG/XLSX、最大10MB）
- 🆕 OCRキャッシュシステム（高速処理）
- 🆕 API Key安全管理（バックエンドのみ）

#### 👥 従業員管理モジュール
- ✅ 4種類のID管理：
  - **UNS-XXXX**: 候補者ID
  - **派遣元ID**: 内部管理番号
  - **Factory-XX**: 工場ID
  - **派遣先社員ID**: 工場での社員番号（編集可能）

#### 🏭 工場管理モジュール（20工場以上対応）
- ✅ JSON形式の工場別設定
- ✅ カスタマイズ可能なシフト（朝番/昼番/夜番）
- ✅ 時給単価の工場別・職種別設定
- ✅ 賞与・手当の設定

#### ⏰ タイムカード管理モジュール
- ✅ 一括アップロード（PDF/スキャン画像）
- ✅ OCR自動処理
- ✅ 編集可能なExcel形式表示
- ✅ 複数工場フォーマット対応

#### 💰 給与計算モジュール
- ✅ 自動計算：
  - 通常時間
  - 残業手当（25%/35%）
  - 深夜手当（22:00-05:00）
  - 休日出勤手当
  - 賞与（ガソリン代、皆勤賞など）
- ✅ 寮費管理（日割り計算対応）
- ✅ 時給と時給単価の比較（利益計算）

#### 📋 申請管理モジュール
- ✅ 有給休暇申請
- ✅ 半日有給
- ✅ 一時帰国申請
- ✅ 退社報告
- ✅ 電子署名機能

#### 📊 ダッシュボード＆レポート
- ✅ 3段階のユーザーレベル：
  - **スーパー管理者**: 全システム管理
  - **管理者**: 工場別管理
  - **コーディネーター**: 閲覧のみ
  - **従業員**: 個人データ閲覧＋申請
- ✅ リアルタイム利益確認
- ✅ 工場別収支管理
- ✅ エクスポート機能

#### 🔔 通知機能
- ✅ メール自動送信
- ✅ LINE/WhatsApp/Messenger（オプション）

---

## 動作環境

### 必要なソフトウェア

- **Windows 10/11** (64bit)
- **Docker Desktop for Windows** 4.0以降
- **最小メモリ**: 4GB（推奨：8GB）
- **ディスク容量**: 20GB以上

### ブラウザ

- Google Chrome（推奨）
- Microsoft Edge
- Firefox
- Safari

---

## インストール手順（Windows）

### ステップ1: Docker Desktopのインストール

1. [Docker Desktop](https://www.docker.com/products/docker-desktop)をダウンロード
2. インストーラーを実行
3. Docker Desktopを起動
4. WSL2が有効になっていることを確認

### ステップ2: プロジェクトの配置

1. `uns-claudejp-api-complete.tar.gz` をダウンロード
2. `D:\` ドライブに配置
3. 展開（解凍）:
   ```
   D:\UNS-JPClaude\
   ```

### ステップ3: コマンドプロンプトを開く

```cmd
cd D:\UNS-JPClaude
```

### ステップ4: インストール実行

```cmd
install-windows.bat
```

スクリプトが自動的に以下を実行します：
- ✅ Docker確認
- ✅ 必要なディレクトリ作成
- ✅ 環境設定ファイル作成
- ✅ Dockerイメージビルド
- ✅ サービス起動

### ステップ5: ブラウザでアクセス

インストール完了後、以下にアクセス：

- **フロントエンド**: http://localhost:3000
- **API管理画面**: http://localhost:8000/api/docs

---

## 初期設定

### 1. 環境変数の編集

`D:\UNS-JPClaude\.env` を編集：

```env
# データベースパスワード（必須変更）
DB_PASSWORD=your_secure_password_here

# セキュリティキー（必須変更）
SECRET_KEY=your_secret_key_here

# メール設定（オプション）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# LINE通知（オプション）
LINE_NOTIFY_ENABLED=true
LINE_NOTIFY_TOKEN=your_line_token
```

### 2. サービス再起動

```cmd
cd D:\UNS-JPClaude
docker-compose restart
```

### 3. 初回ログイン

**デフォルトアカウント**:
- ユーザー名: `admin`
- パスワード: `admin123`

⚠️ **重要**: 初回ログイン後、必ずパスワードを変更してください！

---

## 使い方

### 1. 候補者登録（履歴書処理）

```
1. 候補者 → 書類をアップロード
   ├── 履歴書（PDF/JPG）
   ├── 在留カード
   └── 免許証

2. システム → OCR自動処理
   ├── データ抽出
   ├── フォーム自動入力
   └── ID付与: UNS-1000

3. 管理者 → 確認・承認
   └── ステータス: 承認済み
```

### 2. 入社手続き（入社届）

```
1. 承認済み候補者 → 入社届作成
2. 労働情報入力
   ├── 配属工場
   ├── 時給
   ├── 職種
   └── 寮（該当する場合）
3. ID自動生成
   ├── 派遣元ID: 1001
   ├── 工場ID: Factory-02
   └── 派遣先社員ID: （編集可能）
```

### 3. タイムカード管理

```
1. 一括アップロード
   ├── 工場のPDF/画像をアップロード
   └── OCRで自動処理

2. 確認・修正
   ├── Excel形式の表で確認
   ├── エラーを修正
   └── 承認

3. 自動計算
   ├── 通常時間
   ├── 残業時間
   ├── 深夜手当
   └── 休日出勤
```

### 4. 給与計算

```
計算式:
- 基本給 = 時給 × 通常時間
- 残業手当 = 時給 × 残業時間 × 1.25
- 深夜手当 = 時給 × 深夜時間 × 1.25
- 休日手当 = 時給 × 休日時間 × 1.35
- 賞与（ガソリン代、皆勤賞など）
- 控除（寮費など）

= 手取り給与
```

### 5. 申請処理（有給など）

```
従業員:
1. ログイン → マイポータル
2. 新規申請
   ├── 種類: 有給休暇/半日有給/一時帰国
   ├── 日付
   └── 理由

管理者:
3. 申請確認
4. 承認/却下
5. 自動通知
```

---

## トラブルシューティング

### エラー: データベースに接続できない

```cmd
# データベース状態確認
docker-compose ps

# データベースログ確認
docker-compose logs db

# データベース再起動
docker-compose restart db
```

### エラー: OCRが動作しない

```cmd
# バックエンドでTesseract確認
docker-compose exec backend tesseract --version

# イメージ再ビルド
docker-compose build backend
docker-compose up -d backend
```

### エラー: ファイルがアップロードできない

```cmd
# アップロードフォルダの権限確認
# uploadsフォルダを確認

# ディスク容量確認
dir D:\
```

### フロントエンドが読み込まれない

```cmd
# フロントエンドログ確認
docker-compose logs frontend

# フロントエンド再ビルド
docker-compose build frontend
docker-compose up -d frontend
```

### 管理者パスワードリセット

```cmd
# データベースに接続
docker-compose exec db psql -U uns_admin -d uns_claudejp

# パスワード更新（admin123にリセット）
UPDATE users SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbW4t.5u2' WHERE username = 'admin';
```

---

## 便利なコマンド

### Docker Compose操作

```cmd
# リアルタイムログ表示
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f backend

# サービス停止
docker-compose stop

# サービス起動
docker-compose start

# サービス再起動
docker-compose restart

# イメージ再ビルド
docker-compose build

# 全削除（注意！）
docker-compose down -v
```

### データベースバックアップ

```cmd
# バックアップ作成
docker-compose exec db pg_dump -U uns_admin uns_claudejp > backup_%date%.sql

# バックアップ復元
type backup_20250104.sql | docker-compose exec -T db psql -U uns_admin uns_claudejp
```

### システム更新

```cmd
cd D:\UNS-JPClaude

# 最新版取得（Gitを使用している場合）
git pull

# イメージ再ビルド
docker-compose build

# 新バージョンで再起動
docker-compose up -d
```

---

## サポート・お問い合わせ

**UNS企画**
- ウェブサイト: https://uns-kikaku.com
- メール: support@uns-kikaku.com
- 電話: 052-XXX-XXXX

**技術ドキュメント**:
- API仕様書: http://localhost:8000/api/docs
- 開発者ガイド: `/docs`フォルダ内

---

## ライセンス

UNS企画 © 2025 All Rights Reserved

---

**UNS-ClaudeJP 2.0へようこそ！** 🚀

---

## 🆕 バージョン 2.0 の新機能

### システムの改善点

1. **ハイブリッドOCRシステム**
   - Gemini API (最高精度)
   - Google Cloud Vision API (バックアップ)
   - Tesseract OCR (オフライン対応)
   - 自動キャッシュで高速処理

2. **セキュリティ強化**
   - API Keyをバックエンドに移動
   - フロントエンドでの露出を完全排除
   - エンタープライズレベルのセキュリティ

3. **新しいサービス**
   - 自動通知システム（Email + LINE）
   - 給与自動計算（日本の労働法準拠）
   - Excelインポート/エクスポート
   - 自動レポート生成（グラフ付き）

4. **パフォーマンス向上**
   - OCR処理速度の大幅改善
   - メモリ使用量の最適化
   - データベースクエリの高速化
