# 🚀 クイックスタートガイド - Windows版

## ⚡ 5分でセットアップ

### 📋 前提条件

- ✅ Windows 10/11（64bit）
- ✅ Docker Desktop for Windows

---

## 🔧 インストール手順

### 1️⃣ Docker Desktopのインストール

まだインストールしていない場合:

1. https://www.docker.com/products/docker-desktop からダウンロード
2. インストーラーを実行
3. Docker Desktopを起動

### 2️⃣ プロジェクトの配置

```cmd
D:\UNS-JPClaude\
```

このフォルダに全ファイルを展開

### 3️⃣ インストール実行

コマンドプロンプトを開いて：

```cmd
cd D:\UNS-JPClaude
install-windows.bat
```

自動的にインストールが開始されます！

### 4️⃣ ブラウザでアクセス

インストール完了後：

**アプリケーション**: http://localhost:3000

**ログイン情報**:
- ユーザー名: `admin`
- パスワード: `admin123`

---

## ⚙️ 初期設定（重要！）

### 1. パスワード変更

初回ログイン後、必ずパスワードを変更：

```
プロフィール → 設定 → パスワード変更
```

### 2. 環境設定ファイル編集

`D:\UNS-JPClaude\.env` を編集：

```env
# セキュリティ（必須変更）
DB_PASSWORD=強力なパスワードに変更
SECRET_KEY=ランダムな文字列に変更

# メール設定（オプション）
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=アプリパスワード
```

### 3. サービス再起動

```cmd
cd D:\UNS-JPClaude
docker-compose restart
```

---

## 🎯 基本的な使い方

### 候補者登録

```
1. 「候補者」→「新規登録」
2. 履歴書をアップロード（PDF/JPG）
3. OCRが自動でデータ抽出
4. 確認して保存
5. ID自動生成: UNS-1000
```

### 入社手続き

```
1. 承認済み候補者を選択
2. 「入社届作成」をクリック
3. 労働条件を入力:
   - 工場: Factory-01
   - 時給: 1500円
   - 職種: 製造
4. 保存 → 自動的にIDが生成
```

### タイムカード処理

```
1. 「タイムカード」→「アップロード」
2. 工場のPDFをアップロード
3. OCR処理を確認
4. エラーがあれば修正
5. 「承認」をクリック
```

### 給与計算

```
1. 「給与」→「月次計算」
2. 年月を選択
3. 「計算実行」
4. 結果を確認:
   - 基本給
   - 残業手当
   - 深夜手当
   - 控除
   - 手取り額
   - 会社利益
5. 「承認」
```

---

## 🛠️ よくある問題と解決方法

### Q: Docker Desktopが起動しない

**A**: 
1. Windows再起動
2. WSL2が有効か確認
3. Docker Desktopを再インストール

### Q: ポート3000/8000が使用中

**A**:
```cmd
# 使用中のポートを確認
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# プロセスを終了
taskkill /PID [プロセスID] /F
```

### Q: OCRが日本語を認識しない

**A**:
```cmd
# バックエンド再ビルド
docker-compose build backend
docker-compose up -d backend
```

### Q: データベースエラー

**A**:
```cmd
# データベース再起動
docker-compose restart db

# ログ確認
docker-compose logs db
```

---

## 📱 モバイルアクセス

### 同じネットワーク内の他デバイスからアクセス

1. PCのIPアドレスを確認:
   ```cmd
   ipconfig
   ```

2. スマホ/タブレットのブラウザで:
   ```
   http://[PCのIP]:3000
   ```

例: `http://192.168.1.100:3000`

---

## 🔄 日常操作

### システム起動

```cmd
cd D:\UNS-JPClaude
docker-compose start
```

### システム停止

```cmd
cd D:\UNS-JPClaude
docker-compose stop
```

### ログ確認

```cmd
cd D:\UNS-JPClaude
docker-compose logs -f
```

### データバックアップ

```cmd
cd D:\UNS-JPClaude
docker-compose exec db pg_dump -U uns_admin uns_claudejp > backup.sql
```

---

## 📞 サポート

問題が解決しない場合:

**UNS企画サポート**
- メール: support@uns-kikaku.com
- 電話: 052-XXX-XXXX
- 営業時間: 平日 9:00-18:00

---

## ✅ チェックリスト

インストール後、以下を確認：

- [ ] Docker Desktopが起動している
- [ ] http://localhost:3000 にアクセスできる
- [ ] ログインできる（admin/admin123）
- [ ] パスワードを変更した
- [ ] .envファイルを編集した
- [ ] テスト候補者を登録できた

---

**準備完了！UNS-ClaudeJPをご活用ください！** 🎉
