import time
import json
import requests
from bs4 import BeautifulSoup

# GitHubのGoogleリポジトリページのURL
url = "https://github.com/orgs/google/repositories"
# Webページにアクセスする際に普通のブラウザからのアクセスを証明
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

print("データ取得を開始します...")
time.sleep(1) # サーバー負荷の軽減
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
        star_count = repo.get("stargazerCount", 0)

        # 取得したデータのリポジトリ名、言語、スター数を表示
        print(f"リポジトリ名: {repo_name}")
        print(f"  言語: {language}")
        print(f"  スター数: {star_count}")
        print("-" * 30)
else:
    print("データが埋め込まれたタグが見つかりませんでした。")
