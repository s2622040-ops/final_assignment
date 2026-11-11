import time
import json
import requests
import sqlite3
from bs4 import BeautifulSoup

# GitHubのGoogleリポジトリページのURL
url = "https://github.com/orgs/google/repositories"
# Webページにアクセスする際に普通のブラウザからのアクセスを証明
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# ===================================================
    # データベースの処理
    # ===================================================

db_name = "google_repos.db" # データベース名
conn = sqlite3.connect(db_name) # データベースに接続
cursor = conn.cursor() # カーソルを作成

# テーブルが存在する場合は削除し、新たに作成
cursor.execute("DROP TABLE IF EXISTS repositories")
cursor.execute("""
    CREATE TABLE repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT, // 自動で連番を振る
        name TEXT, // リポジトリ名
        language TEXT, // 使用言語
        star_count INTEGER // スター数
    )
""")

print("データ取得を開始します...")
# ==================================
# ページ切り替え
# ==================================
page = 1
total_pages = 1  # 初期値として1ページ目を設定

# 現在のページ番号が総ページ数以下である限りループする
while page <= total_pages:
    # GitHubのGoogleリポジトリページのURLにページ番号を付加
    url = f"https://github.com/orgs/google/repositories?page={page}"

    time.sleep(1) # サーバー負荷の軽減
    print(f"{page}ページ目のデータを取得中...")

    # webページのHTMLを取得
    response = requests.get(url, headers=headers)
    # BeautifulSoupを使ってHTMLを解析
    soup = BeautifulSoup(response.text, "html.parser")


    target_script = None
    # html内のscriptタグをリストとして取得、for文で1つずつ確認する
    for script in soup.find_all("script"):
        # scriptタグの中の"payload"が含まれている確認
        if script.string and '"payload":{"orgReposPageRoute"' in script.string:
            target_script = script # "payload"を含むscriptタグを取得
            break

    if target_script:
        # JSON形式の文字列をPythonの辞書型に変換
        data = json.loads(target_script.string)

        # 最初の1ページ目のデータ取得時に総ページ数を取得
        if page == 1:
            total_pages = data["payload"]["orgReposPageRoute"].get("pageCount", 1)  
            print(f"全{total_pages}ページのリポジトリデータを取得します\n")
    
        # payloadの中のorgReposPageRouteのrepositoriesを取得
        repos = data["payload"]["orgReposPageRoute"]["repositories"]

        print(f"{len(repos)}件のリポジトリデータを抽出しました！\n") # 確認用

    

        # 取得したリポジトリデータを1件ずつ表示
        for repo in repos:
            # "name"キーが存在しない場合は"不明"を代入
            repo_name = repo.get("name", "不明")

            # "primaryLanguage"キーを取得
            lang_data = repo.get("primaryLanguage")
            # "primaryLanguage"キーが存在しない場合は"None"を代入
            language = lang_data.get("name") if lang_data else "None"

            # "stargazerCount"キーを取得(存在しない場合は0を代入)
            star_count = repo.get("starsCount", 0)

            cursor.execute("""
                INSERT INTO repositories (name, language, star_count)
                VALUES (?, ?, ?)
            """, (repo_name, language, star_count))
        page += 1  # 次のページに進む
    else:
        print(f"{page}ページ目のデータが見つかりませんでした。")
        break

# データベースに保存
conn.commit()
print("データベースの保存が完了しました\n")

print("=== 保存したデータをSELECT文で表示 ===")
# 保存したデータをSELECT文で表示
cursor.execute("SELECT name, language, star_count FROM repositories")
# 取得したデータを1件ずつ表示
rows = cursor.fetchall()
# 各列データを表示する際に、リポジトリ名を30文字、言語を12文字で整列させる
for row in rows:
    print(f"リポジトリ名: {row[0]:<30}, 言語: {row[1]:<12}, スター数: {row[2]}")

conn.close() # データベースの接続を閉じる

        # 取得したデータのリポジトリ名、言語、スター数を表示
        # print(f"リポジトリ名: {repo_name}")
        # print(f"  言語: {language}")
        # print(f"  スター数: {star_count}")
        # print("-" * 30)