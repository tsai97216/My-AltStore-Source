import os
import json
import requests
import hashlib

# === 個人化設定區 ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FILENAME = "apps.json"
# 你的 GitHub 帳號
YOUR_GITHUB_ID = "tsai97216" 
# 商店顯示名稱
DISPLAY_NAME = "Chi" 

SOURCE_URL = f"https://{YOUR_GITHUB_ID}.github.io/My-AltStore-Source/{FILENAME}"

# 1. 商店圖標 (使用 .PNG 大寫連結)
SOURCE_ICON_URL = f"https://raw.githubusercontent.com/{YOUR_GITHUB_ID}/My-AltStore-Source/main/source_icon.PNG"

# 2. 顏色設定 (嫩綠色)
COLOR_PILI = "7DCEA0" 

# --- PiliPlus 設定 ---
PILI_CONFIG = {
    "repo": "bggRGjQaUbCoE/PiliPlus",
    "name": "PiliPlus",
    "bundleID": "com.bgg.piliplus",
    "icon": "https://raw.githubusercontent.com/bggRGjQaUbCoE/PiliPlus/main/assets/images/logo/desktop/logo_large.png",
    "subtitle": "第三方 Bilibili iOS 客戶端增強版",
    "desc": "PiliPlus 提供自動全螢幕、音量均衡、彈幕過濾等豐富功能，帶給你更純粹的觀影體驗。"
}

def get_sha1(url):
    print(f"正在計算 Hash: {url}")
    response = requests.get(url, stream=True)
    sha1 = hashlib.sha1()
    for chunk in response.iter_content(chunk_size=8192):
        sha1.update(chunk)
    return sha1.hexdigest()

def get_pili_data():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    api_url = f"https://api.github.com/repos/{PILI_CONFIG['repo']}/releases/latest"
    
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        print(f"❌ 無法獲取 PiliPlus 資訊")
        return None

    data = res.json()
    assets = data.get("assets", [])
    ipa_asset = next((a for a in assets if a["name"].lower().endswith(".ipa")), None)

    if not ipa_asset:
        print(f"❌ 找不到 IPA 檔案")
        return None

    print(f"✅ 發現最新版本: {data['tag_name']}")

    return {
        "name": PILI_CONFIG["name"],
        "bundleIdentifier": PILI_CONFIG["bundleID"],
        "developerName": PILI_CONFIG["repo"].split('/')[0],
        "subtitle": PILI_CONFIG["subtitle"],
        "localizedDescription": PILI_CONFIG["desc"],
        "iconURL": PILI_CONFIG["icon"],
        "tintColor": COLOR_PILI,
        "category": "entertainment",
        "screenshots": [],
        "versions": [
            {
                "version": data["tag_name"].replace('v', ''),
                "date": data["published_at"][:10],
                "localizedDescription": data["body"][:1000] if data["body"] else "自動同步 GitHub 最新版本",
                "downloadURL": ipa_asset["browser_download_url"],
                "size": ipa_asset["size"],
                "sha1hash": get_sha1(ipa_asset["browser_download_url"])
            }
        ]
    }

def update_source():
    print(f"🚀 正在更新 {DISPLAY_NAME} 的私人商店...")
    pili_data = get_pili_data()
    
    apps_list = [pili_data] if pili_data else []

    source_data = {
        "name": f"{DISPLAY_NAME} 的私人商店",
        "identifier": f"com.{DISPLAY_NAME.lower()}.custom.source",
        "sourceURL": SOURCE_URL,
        "subtitle": "精選 iOS 增強版 App",
        "description": f"這是 {DISPLAY_NAME} 維護的個人來源，目前專注於提供 PiliPlus 的穩定更新。",
        "website": f"https://github.com/{YOUR_GITHUB_ID}/My-AltStore-Source",
        "iconURL": SOURCE_ICON_URL,
        "featuredApps": [app["bundleIdentifier"] for app in apps_list],
        "apps": apps_list,
        "news": []
    }

    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2, ensure_ascii=False)
    print(f"🎉 商店已簡化完成，目前僅保留 PiliPlus。")

if __name__ == "__main__":
    update_source()
