# TimeFiller (勤務データ自動入力ツール)

CSVファイルの勤務データをExcelファイルに自動入力するツールです。
AWS EC2へのデプロイに対応し、ブラウザから簡単に利用できます。

## 機能

- **自動入力**: CSVファイルからExcelの業務報告書へデータを自動転記
- **自動計算**: 出勤日数、総稼働時間を自動計算
- **ファイル名自動生成**: 氏名に基づいたファイル名でダウンロード可能
- **セキュリティ**: 簡易パスワード認証機能搭載
- **バックアップ**: 処理実行時にバックアップを自動作成（ローカル実行時）

![alt text](<スクリーンショット 2025-11-20 午後2.24.25.png>)

## ファイル構成

```
kintai/
├── app.py                        # Streamlit Webアプリ
├── attendance_auto_input.py      # コアロジック
├── config.py                     # 設定ファイル
├── DEPLOY_EC2.md                 # AWS EC2デプロイ手順書
├── Dockerfile                    # コンテナ化用設定
├── requirements.txt              # 依存ライブラリ
└── README.md                     # このファイル
```

## 使用方法 (Webアプリ)

### 1. ローカルでの実行

```bash
# 依存ライブラリのインストール
pip install -r requirements.txt

# アプリの起動 (パスワードなし)
streamlit run app.py

# アプリの起動 (パスワードあり)
export APP_PASSWORD=your_password
streamlit run app.py
```

### 2. AWS EC2へのデプロイ

詳細な手順は [DEPLOY_EC2.md](DEPLOY_EC2.md) を参照してください。

## 使用方法 (コマンドライン)

従来のコマンドライン実行も可能です。

```bash
python3 attendance_auto_input.py [CSVファイル] [Excelファイル] [-o 出力ファイル]
```

## 必要な環境

- Python 3.12 以上
- 必要なライブラリ (requirements.txt参照):
  - streamlit
  - pandas
  - openpyxl
  - numpy

## カスタマイズ

`config.py`ファイルを編集することで、Excelの列位置や休日区分などをカスタマイズできます。

## 更新履歴

- **v2.0.0**: Webアプリ化 (Streamlit)、AWSデプロイ対応、パスワード認証追加
- **v1.0.0**: 初回リリース (コマンドライン版)
