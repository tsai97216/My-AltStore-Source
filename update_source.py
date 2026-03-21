import os
import json
import requests
import hashlib

# === 個人化設定區 ===
REPO = "bggRGjQaUbCoE/PiliPlus"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FILENAME = "apps.json"
YOUR_ID = "tsai97216"
SOURCE_URL = f"https://{YOUR_ID}.github.io/My-AltStore-Source/{FILENAME}"

# 1. 商店與 App 圖標
SOURCE_ICON = f"https://raw.githubusercontent.com/{YOUR_ID}/My-AltStore-Source/main/source_icon.png"
APP_ICON = "https://raw.githubusercontent.com/bggRGjQaUbCoE/PiliPlus/main/assets/images/logo/desktop/logo_large.png"

def get_sha1(url):
    print(f"正在計算檔案 Hash: {url}")
    response = requests.get(url, stream=True)
    sha1 = hashlib.sha1()
    for chunk in response.iter_content(chunk_size=8192):
        sha1.update(chunk)
    return int(sha1.hexdigest(), 16), sha1.hexdigest()

def update():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    api_url = f"https://api.github.com/repos/{REPO}/releases/latest"
    
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        print(f"❌ API 請求失敗")
        return

    data = res.json()
    assets = data.get("assets", [])
    ipa_asset = next((a for a in assets if a["name"].lower().endswith(".ipa")), None)

    if not ipa_asset:
        print("❌ 找不到 IPA 檔案")
        return

    _, sha1_str = get_sha1(ipa_asset["browser_download_url"])

    # --- 依照 Aidoku 格式建構 App 資訊 ---
    piliplus_app = {
        "name": "PiliPlus",
        "bundleIdentifier": "com.bgg.piliplus",
        "developerName": "bggRGjQaUbCoE",
        "subtitle": "第三方 Bilibili iOS 客戶端增強版",
        "localizedDescription": "PiliPlus 是一款強大的 Bilibili 第三方客戶端，提供自動全螢幕、音量均衡、彈幕過濾等豐富功能，帶給你更純粹的觀影體驗。",
        "iconURL": APP_ICON,
        "tintColor": "fb7299", # Bilibili 粉色
        "category": "entertainment",
        "screenshots": [
            # 如果你有截圖連結，可以像下面這樣加入
            # {"imageURL": "https://example.com/ss1.png", "width": 450, "height": 908}
        ],
        "appPermissions": {
            "entitlements": ["aps-environment"],
            "privacy": {
                "NSPhotoLibraryUsageDescription": "需要權限以儲存圖片或影片",
                "NSLocalNetworkUsageDescription": "需要權限以連接本地伺服器"
            }
        },
        "versions": [
            {
                "version": data["tag_name"].replace('v', ''),
                "date": data["published_at"][:10],
                "localizedDescription": data["body"][:2000], # 抓取 Release 內容
                "downloadURL": ipa_asset["browser_download_url"],
                "size": ipa_asset["size"],
                "sha1hash": sha1_str
            }
        ]
    }

    # --- 商店頂層資訊 ---
    source_data = {
        "name": "Tsai 的私人商店",
        "identifier": f"com.{YOUR_ID}.custom.source",
        "sourceURL": SOURCE_URL,
        "subtitle": "收集好用的 iOS 增強版 App",
        "description": "這是 Tsai 維護的個人 AltStore 來源，專注於提供最新、最穩定的修改版 App 更新。",
        "website": f"https://github.com/{YOUR_ID}/My-AltStore-Source",
        "iconURL": SOURCE_ICON,
        "featuredApps": ["com.bgg.piliplus"],
        "apps": [piliplus_app],
        "news": []
    }

    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2, ensure_ascii=False)
    
    print(f"🎉 完美格式已生成！")

if __name__ == "__main__":
    update()
