---
description: AWS EC2へのデプロイ手順
---

# AWS EC2 デプロイ手順書 (TimeFiller)

このガイドでは、**TimeFiller** (旧: 勤務データ自動入力ツール) を AWS EC2 インスタンスにデプロイする方法を説明します。

## 事前準備

1.  **AWS アカウント**: 有効な AWS アカウントが必要です。
2.  **キーペア**: AWS コンソール (EC2 > キーペア) で SSH キーペア (例: `kintai-key.pem`) を作成し、ダウンロードしておきます。

## 手順 1: EC2 インスタンスの起動

1.  **EC2 ダッシュボード** > **インスタンスを起動** をクリックします。
2.  **名前**: `TimeFiller` (任意)
3.  **OS イメージ**: `Ubuntu Server 24.04 LTS` (無料枠対象) または `Amazon Linux 2023`。
4.  **インスタンスタイプ**:
    *   `t2.micro` または `t3.micro` (無料枠がある場合)。
    *   `t4g.nano` (最も安価なオプション。ARMアーキテクチャ)。
5.  **キーペア**: 作成したキーペアを選択します。
6.  **ネットワーク設定**:
    *   SSH トラフィック: `自分の IP` から許可。
    *   インターネットからの HTTP トラフィックを許可。
    *   **セキュリティグループ**:
        *   カスタム TCP ポート **8501** を `0.0.0.0/0` (任意の場所) から許可。
        *   **HTTPS** (ポート **443**) を `0.0.0.0/0` から許可 (HTTPS化する場合)。
        *   *アプリ側でパスワード認証を行うため、IP制限は必須ではありません。*
7.  **ストレージ**: 8GB gp3 (デフォルトでOK)。
8.  **インスタンスを起動** をクリックします。

## 手順 2: インスタンスへの接続

ターミナルで以下のコマンドを実行して接続します。

```bash
# キーペアの権限を変更（必須）
chmod 400 path/to/kintai-key.pem

# SSH接続 (Amazon Linux 2023の場合はec2-user、Ubuntuの場合はubuntu)
ssh -i path/to/kintai-key.pem ec2-user@<パブリックIPアドレス>
```

## 手順 3: 環境セットアップ (Docker)

EC2 インスタンスに接続後、以下のコマンドを実行して Docker をインストールします。

### Amazon Linux 2023 の場合

```bash
# システムの更新
sudo dnf update -y

# Dockerのインストール
sudo dnf install -y docker

# Dockerサービスの起動と自動起動設定
sudo systemctl start docker
sudo systemctl enable docker

# docker-composeのインストール (HTTPS化に必要)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 現在のユーザーをdockerグループに追加
sudo usermod -aG docker $USER

# グループ変更を反映させるために一度ログアウト
exit
```

### Ubuntu の場合

```bash
# Dockerのインストール
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER

# docker-composeのインストール (HTTPS化に必要)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# グループ変更を反映させるために一度ログアウト
exit
```

再度 SSH で接続します：
```bash
# Amazon Linux 2023
ssh -i path/to/kintai-key.pem ec2-user@<パブリックIPアドレス>

# Ubuntu
ssh -i path/to/kintai-key.pem ubuntu@<パブリックIPアドレス>
```

## 手順 3.5: GitHub との接続設定 (セキュリティ推奨: Deploy Key)

サーバーから GitHub リポジトリに安全にアクセスするために、**Deploy Key** を使用します。
これにより、このサーバーには「対象リポジトリへの読み取り権限」のみが付与され、個人のアカウント全体へのアクセス権は与えられません（最小権限の原則）。

1.  **SSHキーの作成**:
    EC2 サーバー上で以下のコマンドを実行し、キーを作成します。
    ```bash
    # -f でファイル名を指定 (例: ~/.ssh/github_deploy_key)
    ssh-keygen -t ed25519 -C "ec2-deploy-key" -f ~/.ssh/github_deploy_key
    ```
    (パスフレーズは空のままでEnterを2回押します)

2.  **SSH設定ファイルの作成**:
    GitHub 接続時にこのキーを使うように設定します。
    ```bash
    # ~/.ssh/config ファイルを作成/追記
    cat << EOF >> ~/.ssh/config
    Host github.com
      IdentityFile ~/.ssh/github_deploy_key
      User git
    EOF
    
    # 権限を修正
    chmod 600 ~/.ssh/config
    ```

3.  **公開鍵の表示**:
    作成された公開鍵を表示し、コピーします。
    ```bash
    cat ~/.ssh/github_deploy_key.pub
    ```
    （`ssh-ed25519 ...` から始まる文字列をコピーしてください）

4.  **GitHub への登録 (Deploy Key)**:
    *   対象の GitHub リポジトリを開きます。
    *   **Settings** > **Deploy keys** > **Add deploy key**。
    *   **Title**: `EC2 TimeFiller` (任意)
    *   **Key**: コピーした公開鍵を貼り付けます。
    *   **Allow write access**: チェックは**外したまま**にします（読み取り専用）。
    *   **Add key** をクリック。

5.  **接続テスト**:
    ```bash
    ssh -T git@github.com
    ```
    `Hi username/repo! You've successfully authenticated...` と表示されればOKです。

## 手順 4: アプリケーションのデプロイ

### 方法 A: Git クローン (推奨)
コードを GitHub 等にプッシュしている場合：
```bash
git clone <リポジトリURL> TimeFiller
cd TimeFiller
docker build -t timefiller .
# アプリ側でパスワード認証を行わないため、セキュリティグループで接続元IPを制限することを強く推奨します。
# --restart unless-stopped を追加して、再起動時も自動で立ち上がるようにします
docker run -d -p 8501:8501 --restart unless-stopped --name timefiller-container timefiller
```

### 方法 B: ファイルのアップロード (SCP)
Git を使わない場合、ローカルマシンからファイルを直接アップロードします：
```bash
# 【ローカルマシン】で実行してください
# Amazon Linux 2023の場合
scp -i path/to/kintai-key.pem -r path/to/kintai/* ec2-user@<パブリックIPアドレス>:~/TimeFiller/

# Ubuntuの場合
scp -i path/to/kintai-key.pem -r path/to/kintai/* ubuntu@<パブリックIPアドレス>:~/TimeFiller/
```

その後、EC2 上で以下を実行します：
```bash
cd TimeFiller
docker build -t timefiller .
# -e APP_PASSWORD=... でパスワードを設定します
# --restart unless-stopped を追加して、再起動時も自動で立ち上がるようにします
docker run -d -p 8501:8501 -e APP_PASSWORD=your_secure_password --restart unless-stopped --name timefiller-container timefiller
```

## 手順 5: アプリケーションへのアクセス

ブラウザを開き、以下のアドレスにアクセスしてください：
`http://<パブリックIPアドレス>:8501`

## 手順 5: HTTPS (SSL/TLS) 化 (推奨)

Let's Encrypt を使用して、無料で HTTPS 化を行います。

### 1. ドメインの準備
*   DuckDNS などのサービスでドメインを取得します (例: `timefiller.duckdns.org`)。
*   取得したドメインの **Aレコード** を、EC2 インスタンスの **パブリックIPアドレス** に設定します。

### 2. 設定ファイルの準備
以下のファイルがプロジェクトに含まれていることを確認し、必要に応じて編集します。

**`docker-compose.yml`**:
EC2上では `buildx` が使えない場合があるため、`image: timefiller:latest` を使用し、事前にビルドしたイメージを使う構成にします。

```yaml
version: '3'

services:
  app:
    image: timefiller:latest # ビルド済みイメージを使用
    container_name: timefiller-app
    restart: unless-stopped
    ports:
      - "8501:8501"
    environment:
      - APP_PASSWORD=${APP_PASSWORD}

  nginx:
    image: nginx:1.25-alpine
    container_name: timefiller-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - app

  certbot:
    image: certbot/certbot
    container_name: timefiller-certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
```

**`nginx/nginx.conf`**:
ドメイン名 (`timefiller.duckdns.org` など) が正しいか確認してください。
**注意: `ssl_certificate` のパスにスペースが入らないようにしてください。**

```nginx
server {
    listen 80;
    server_name your-domain.com; # 変更
    # ... (省略) ...
}

server {
    listen 443 ssl;
    server_name your-domain.com; # 変更

    # パスに注意！スペース厳禁
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... (省略) ...
}
```

### 3. 証明書の取得と起動
初回は `init-letsencrypt.sh` スクリプトを使用して証明書を取得します。

1.  **イメージのビルド**:
    ```bash
    docker build -t timefiller:latest .
    ```

2.  **スクリプトの編集**:
    `init-letsencrypt.sh` 内の `domains` と `email` を自分のものに書き換えます。

3.  **スクリプトの実行**:
    ```bash
    chmod +x init-letsencrypt.sh
    sudo APP_PASSWORD=your_password ./init-letsencrypt.sh
    ```

成功すると、Nginx とアプリが起動します。ブラウザで `https://your-domain.com` にアクセスして確認してください。

**トラブルシューティング:**
*   `Connection refused`: セキュリティグループでポート443が開いているか確認してください。
*   `SSL_ERROR_SYSCALL`: `nginx.conf` の証明書パスが間違っている可能性があります（スペースなど）。
*   `nginx` が起動しない: `docker logs timefiller-nginx` でログを確認してください。証明書がない状態で SSL 設定が有効になっていると起動しません（スクリプトが自動処理しますが、手動設定時は注意）。

### 4. 証明書の自動更新設定
証明書の有効期限は90日です。自動更新するために、cron ジョブを設定します。

**Amazon Linux 2023 の場合、cron がインストールされていないことがあります。**
その場合は、まずインストールしてください：

```bash
# cron のインストールと起動
sudo dnf install -y cronie
sudo systemctl start crond
sudo systemctl enable crond
```

次に、crontab を設定します：

```bash
# crontabを開く
crontab -e
```

以下の行を追加して保存します（毎日深夜3時に更新チェック）。
```
0 3 * * * cd /home/ec2-user/TimeFiller && /usr/local/bin/docker-compose run --rm certbot renew && /usr/local/bin/docker-compose exec nginx nginx -s reload
```

## 手順 6: インスタンスの停止 (コスト節約)

使用しない時は必ず停止してください。

1.  EC2 ダッシュボードへ移動。
2.  インスタンスを選択 > **インスタンスの状態** > **インスタンスを停止**。
3.  使う時に **インスタンスを開始** します。
    *   *注意: Elastic IP を使っていない場合、再起動時にパブリック IP アドレスが変わります。*

## 手順 7: アプリケーションの更新

コードを変更して GitHub にプッシュした後、EC2 上で反映させる手順です。

```bash
cd TimeFiller

# 1. 最新コードの取得
git pull

# 2. イメージの再ビルド
docker build -t timefiller:latest .

# 3. コンテナの再作成（新しいイメージで起動）
docker-compose up -d

# (オプション) 古いイメージの削除
docker image prune -f
```
※ `nginx.conf` を変更した場合は、さらに `docker-compose restart nginx` も実行してください。
