import os
import json
import requests
import hashlib

# === 設定區 ===
REPO = "bggRGjQaUbCoE/PiliPlus"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FILENAME = "apps.json"
YOUR_ID = "tsai97216"

def get_sha1(url):
    print(f"正在計算檔案 Hash: {url}")
    response = requests.get(url, stream=True)
    sha1 = hashlib.sha1()
    for chunk in response.iter_content(chunk_size=8192):
        sha1.update(chunk)
    return sha1.hexdigest()

def update():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    api_url = f"https://api.github.com/repos/{REPO}/releases/latest"
    
    print(f"正在連線到 GitHub API...")
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        print(f"❌ 無法讀取 GitHub API: {res.status_code}")
        return

    data = res.json()
    assets = data.get("assets", [])
    ipa_asset = next((a for a in assets if a["name"].endswith(".ipa")), None)

    if not ipa_asset:
        print("❌ 在 Release 中找不到 .ipa 檔案")
        return

    print(f"✅ 找到最新版本: {data['tag_name']}")

    # 建立 AltStore 格式
    new_app = {
        "name": "PiliPlus",
        "bundleIdentifier": "com.bgg.piliplus", # 如果不對，安裝後 AltStore 會自動修正
        "developerName": "bggRGjQaUbCoE",
        "version": data["tag_name"],
        "versionDate": data["published_at"],
        "versionDescription": data["body"],
        "downloadURL": ipa_asset["browser_download_url"],
        "localizedDescription": "PiliPlus 增強版",
        "iconURL": "https://raw.githubusercontent.com/bggRGjQaUbCoE/PiliPlus/main/icon.png", # 預設圖示
        "size": ipa_asset["size"],
        "sha1hash": get_sha1(ipa_asset["browser_download_url"])
    }

    source_data = {
        "name": "Tsai 的私人商店",
        "identifier": f"com.{YOUR_ID}.custom.source",
        "apps": [new_app]
    }

    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2, ensure_ascii=False)
    print(f"🎉 成功生成 {FILENAME}！")

if __name__ == "__main__":
    update()
