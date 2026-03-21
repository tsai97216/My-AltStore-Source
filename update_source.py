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

# [修改 1] 商店層級圖標 (Source Icon) - 使用你指定的連結 (注意大寫 PNG)
SOURCE_ICON_URL = f"https://raw.githubusercontent.com/{YOUR_ID}/My-AltStore-Source/main/source_icon.PNG"

# App 層級圖標 (App Icon) - 保持 PiliPlus 高清圖標
APP_ICON_URL = "https://raw.githubusercontent.com/bggRGjQaUbCoE/PiliPlus/main/assets/images/logo/desktop/logo_large.png"

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
    
    print(f"🚀 正在連線至 GitHub API...")
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        print(f"❌ API 請求失敗: {res.status_code}")
        return

    data = res.json()
    assets = data.get("assets", [])
    ipa_asset = next((a for a in assets if a["name"].lower().endswith(".ipa")), None)

    if not ipa_asset:
        print("❌ 在最新 Release 中找不到 IPA 檔案")
        return

    _, sha1_str = get_sha1(ipa_asset["browser_download_url"])

    print(f"✅ 發現新版本: {data['tag_name']}")

    # --- 依照 Aidoku 格式建構 App 資訊 ---
    piliplus_app = {
        "name": "PiliPlus",
        "bundleIdentifier": "com.bgg.piliplus",
        "developerName": "bggRGjQaUbCoE",
        "subtitle": "第三方 Bilibili iOS 客戶端增強版",
        "localizedDescription": "PiliPlus 是一款強大的 Bilibili 第三方客戶端，提供自動全螢幕、音量均衡、彈幕過濾等豐富功能。",
        "iconURL": APP_ICON_URL,
        # [修改 2] 將主題色改為淺綠色 (iOS 標準綠色)
        "tintColor": "34C759", 
        "category": "entertainment",
        "screenshots": [],
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
                "localizedDescription": data["body"][:2000],
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
        "iconURL": SOURCE_ICON_URL, # 使用更新後的商店圖標連結
        "featuredApps": ["com.bgg.piliplus"],
        "apps": [piliplus_app],
        "news": []
    }

    # 強制將結果儲存為 FILENAME (apps.json)
    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2, ensure_ascii=False)
    
    print(f"🎉 綠色版完美格式已生成！")

if __name__ == "__main__":
    update()
