#!/usr/bin/env python3
"""
Xserver 自動デプロイスクリプト（GitHub Actions用）
"""
import paramiko
import os
import sys
import base64

# ========================================
# 接続情報（環境変数から取得）
# ========================================
HOSTNAME = "sv16603.xserver.jp"
PORT = 10022
USERNAME = "xs065599"
PRIVATE_KEY_CONTENT = os.environ.get("XSERVER_PRIVATE_KEY")
REMOTE_DIR = "/home/xs065599/chugaku-matching.com/public_html"

# ========================================
# アップロードするファイル
# ========================================
FILES_TO_UPLOAD = {
    "script.js": "script.js"
}

# ========================================
# 関数定義
# ========================================
def upload_file(sftp, local_path, remote_path, remote_name):
    """ファイルをアップロード"""
    try:
        sftp.put(local_path, remote_path)
        print(f"✅ アップロード成功: {remote_name}")
        return True
    except Exception as e:
        print(f"❌ アップロード失敗: {remote_name} - {e}")
        return False

def main():
    """メイン処理"""
    print("=" * 70)
    print("Xserver 自動デプロイ")
    print("=" * 70)
    print(f"接続先: {HOSTNAME}:{PORT}")
    print(f"ユーザー: {USERNAME}")
    print(f"リモートフォルダ: {REMOTE_DIR}")
    print("=" * 70)
    
    # 秘密鍵の確認
    if not PRIVATE_KEY_CONTENT:
        print("❌ エラー: XSERVER_PRIVATE_KEY が設定されていません")
        sys.exit(1)
    
    # SSH接続
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"\n🔗 SSH接続中...")
        
        # 秘密鍵をBase64デコード
        try:
            decoded_key = base64.b64decode(PRIVATE_KEY_CONTENT).decode('utf-8')
        except:
            # Base64でない場合はそのまま使用
            decoded_key = PRIVATE_KEY_CONTENT
        
        # 秘密鍵を一時ファイルから読み込み
        from io import StringIO
        private_key_file = StringIO(decoded_key)
        private_key = paramiko.RSAKey.from_private_key(private_key_file)
        
        # 接続
        ssh.connect(
            hostname=HOSTNAME,
            port=PORT,
            username=USERNAME,
            pkey=private_key,
            timeout=30
        )
        print("✅ SSH接続成功（公開鍵認証）")
        
        # SFTP接続
        sftp = ssh.open_sftp()
        print("✅ SFTP接続成功")
        
        # ファイルをアップロード
        success_count = 0
        fail_count = 0
        
        print(f"\n📤 ファイルアップロード開始")
        print("-" * 70)
        
        for remote_name, local_name in FILES_TO_UPLOAD.items():
            local_path = local_name
            remote_path = f"{REMOTE_DIR}/{remote_name}"
            
            # ファイルの存在確認
            if not os.path.exists(local_path):
                print(f"⚠️  スキップ: {local_name}（ファイルが見つかりません）")
                fail_count += 1
                continue
            
            # アップロード実行
            if upload_file(sftp, local_path, remote_path, remote_name):
                success_count += 1
            else:
                fail_count += 1
        
        print("-" * 70)
        print(f"\n📊 アップロード結果")
        print(f"✅ 成功: {success_count}件")
        print(f"❌ 失敗: {fail_count}件")
        
        if success_count > 0:
            print(f"\n🎉 デプロイ完了！")
            print(f"🌐 サイト: https://chugaku-matching.com")
        
        sftp.close()
        
        # 失敗があれば終了コード1
        if fail_count > 0:
            sys.exit(1)
        
    except paramiko.AuthenticationException:
        print("❌ 認証失敗: 秘密鍵が正しくありません")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"❌ SSH接続エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)
    finally:
        ssh.close()
        print("\n✅ 接続を終了しました")

if __name__ == "__main__":
    main()
