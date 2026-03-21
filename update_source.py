import os
import json
import requests
import hashlib

# === 個人化設定區 ===
REPO = "bggRGjQaUbCoE/PiliPlus"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FILENAME = "apps.json"
YOUR_ID = "tsai97216"

# 1. 商店層級圖標 (Source Icon) - 你之前上傳的招牌圖
SOURCE_ICON_URL = f"https://raw.githubusercontent.com/{YOUR_ID}/My-AltStore-Source/main/source_icon.png"

# 2. App 層級圖標 (App Icon) - 使用你找的高清 PNG 連結
APP_ICON_URL = "https://raw.githubusercontent.com/bggRGjQaUbCoE/PiliPlus/main/assets/images/logo/desktop/logo_large.png"

def get_sha1(url):
    print(f"正在計算檔案 Hash (這需要一點時間): {url}")
    response = requests.get(url, stream=True)
    sha1 = hashlib.sha1()
    for chunk in response.iter_content(chunk_size=8192):
        sha1.update(chunk)
    return sha1.hexdigest()

def update():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    api_url = f"https://api.github.com/repos/{REPO}/releases/latest"
    
    print(f"🚀 正在從 GitHub 獲取最新版本資訊...")
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        print(f"❌ 無法連線到 GitHub API: {res.status_code}")
        return

    data = res.json()
    assets = data.get("assets", [])
    # 找尋第一個以 .ipa 結尾的檔案
    ipa_asset = next((a for a in assets if a["name"].lower().endswith(".ipa")), None)

    if not ipa_asset:
        print("❌ 在最新版本中找不到任何 .ipa 檔案")
        return

    print(f"✅ 發現新版本: {data['tag_name']}")

    # 建立 AltStore 專用 JSON 格式
    new_app = {
        "name": "PiliPlus",
        "bundleIdentifier": "com.bgg.piliplus",
        "developerName": "bggRGjQaUbCoE",
        "version": data["tag_name"],
        "versionDate": data["published_at"][:10], # 格式化日期為 YYYY-MM-DD
        "versionDescription": data["body"][:1000], # 抓取 Release 說明的前 1000 字
        "downloadURL": ipa_asset["browser_download_url"],
        "localizedDescription": "PiliPlus 增強版：修復自動全螢幕、音量均衡，支持彈幕自定義等功能。",
        "iconURL": APP_ICON_URL,
        "size": ipa_asset["size"],
        "sha1hash": get_sha1(ipa_asset["browser_download_url"])
    }

    source_data = {
        "name": "Tsai 的私人商店",
        "identifier": f"com.{YOUR_ID}.custom.source",
        "iconURL": SOURCE_ICON_URL,
        "apps": [new_app]
    }

    # 存檔
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2, ensure_ascii=False)
    
    print(f"🎉 成功！apps.json 已更新，且圖標設定已生效。")

if __name__ == "__main__":
    update()
