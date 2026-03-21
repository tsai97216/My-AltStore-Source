import os
import json
import requests
import hashlib
import re

# === 個人化設定區 ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
FILENAME = "apps.json"
# 這裡維持你的 GitHub 帳號，用於部署網頁
YOUR_GITHUB_ID = "tsai97216" 
# 商店顯示名稱改為 Chi
DISPLAY_NAME = "Chi" 

SOURCE_URL = f"https://{YOUR_GITHUB_ID}.github.io/My-AltStore-Source/{FILENAME}"

# 1. 商店圖標 (使用你指定的 .PNG 大寫連結)
SOURCE_ICON_URL = f"https://raw.githubusercontent.com/{YOUR_GITHUB_ID}/My-AltStore-Source/main/source_icon.PNG"

# 2. 顏色設定 (嫩綠色)
LIGHT_GREEN = "7DCEA0" 

# --- 待抓取的 App 清單 ---
APPS_TO_TRACK = [
    {
        "repo": "bggRGjQaUbCoE/PiliPlus",
        "name": "PiliPlus",
        "bundleID": "com.bgg.piliplus",
        "icon": "https://raw.githubusercontent.com/bggRGjQaUbCoE/PiliPlus/main/assets/images/logo/desktop/logo_large.png",
        "subtitle": "第三方 Bilibili iOS 客戶端增強版",
        "desc": "提供自動全螢幕、音量均衡、彈幕過濾等豐富功能。",
        "smart_version": False 
    },
    {
        "repo": "6gr8/IGFormat",
        "name": "IGFormat",
        "bundleID": "com.6gr8.IGFormat",
        # [修改] 更新為你找的高清 Raw PNG 連結
        "icon": "https://raw.githubusercontent.com/6gr8/IGFormat/main/IGFormatLogo.png", 
        "subtitle": "Instagram 增強工具",
        "desc": "Instagram 內容排版與功能增強插件。",
        "smart_version": True # 開啟智慧模式：從檔名抓版本號
    }
]

def get_sha1(url):
    print(f"正在下載並計算 Hash: {url}")
    response = requests.get(url, stream=True)
    sha1 = hashlib.sha1()
    for chunk in response.iter_content(chunk_size=8192):
        sha1.update(chunk)
    return sha1.hexdigest()

def extract_version_from_filename(filename, fallback_tag):
    # 使用正則表達式尋找像 1.2.3 或 2.0 這樣的版本號數字
    match = re.search(r'(\d+\.\d+(\.\d+)?)', filename)
    if match:
        return match.group(1)
    return fallback_tag

def get_app_data(config):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    api_url = f"https://api.github.com/repos/{config['repo']}/releases/latest"
    
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        print(f"❌ 無法獲取 {config['name']} 資訊")
        return None

    data = res.json()
    assets = data.get("assets", [])
    ipa_asset = next((a for a in assets if a["name"].lower().endswith(".ipa")), None)

    if not ipa_asset:
        print(f"❌ {config['name']} 找不到 IPA")
        return None

    # --- 版本號智慧處理 ---
    raw_tag = data["tag_name"].replace('v', '')
    ipa_name = ipa_asset["name"]
    
    if config["smart_version"]:
        detected_version = extract_version_from_filename(ipa_name, raw_tag)
        upload_date = ipa_asset["updated_at"][:10].replace('-', '.')
        final_version = f"{detected_version} ({upload_date})"
    else:
        final_version = raw_tag

    return {
        "name": config["name"],
        "bundleIdentifier": config["bundleID"],
        "developerName": config["repo"].split('/')[0],
        "subtitle": config["subtitle"],
        "localizedDescription": config["desc"],
        "iconURL": config["icon"],
        "tintColor": LIGHT_GREEN,
        "category": "social",
        "screenshots": [],
        "versions": [
            {
                "version": final_version,
                "date": ipa_asset["updated_at"][:10],
                "localizedDescription": data["body"][:1000] if data["body"] else "自動偵測更新",
                "downloadURL": ipa_asset["browser_download_url"],
                "size": ipa_asset["size"],
                "sha1hash": get_sha1(ipa_asset["browser_download_url"])
            }
        ]
    }

def update_source():
    all_apps = []
    for config in APPS_TO_TRACK:
        print(f"🚀 正在檢查: {config['name']}...")
        app_data = get_app_data(config)
        if app_data:
            all_apps.append(app_data)

    source_data = {
        "name": f"{DISPLAY_NAME} 的私人商店",
        "identifier": f"com.{DISPLAY_NAME.lower()}.custom.source",
        "sourceURL": SOURCE_URL,
        "subtitle": "收集好用的 iOS 增強版 App",
        "description": f"這是 {DISPLAY_NAME} 維護的個人 AltStore 來源，專注於提供最新、最穩定的修改版 App 更新。",
        "website": f"https://github.com/{YOUR_GITHUB_ID}/My-AltStore-Source",
        "iconURL": SOURCE_ICON_URL,
        "featuredApps": [app["bundleIdentifier"] for app in all_apps],
        "apps": all_apps,
        "news": []
    }

    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2, ensure_ascii=False)
    print(f"🎉 更新完成！IGFormat 已啟用新圖標。")

if __name__ == "__main__":
    update_source()
