import os
import json
from altparse import AltSourceManager, Parser, altsource_from_file

# === 基礎設定區 ===
FILENAME = "apps.json" 
YOUR_GITHUB_USERNAME = "tsai97216" 
SOURCE_NAME = "Tsai 的私人商店" 

# 自動取得 GitHub Actions 提供給腳本的 VIP 通行證
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 1. 確保基礎 JSON 檔案存在，防止讀取失敗
if not os.path.exists(FILENAME):
    initial_source = {
        "name": SOURCE_NAME,
        "identifier": f"com.{YOUR_GITHUB_USERNAME}.custom.source",
        "apps": []
    }
    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(initial_source, f, indent=2, ensure_ascii=False)

# 2. 載入現有資料
src = altsource_from_file(FILENAME)

# 3. 定義你要自動追蹤的 App 列表
apps_to_track = [
    {
        "parser": Parser.GITHUB,
        "kwargs": {
            "repo_author": "bggRGjQaUbCoE",
            "repo_name": "PiliPlus",
            "prefer_date": True,
            # 強制只抓取結尾是 .ipa 的檔案，過濾掉 Android 或電腦版
            "asset_filters": [r".*\.ipa$"] 
        },
        "ids": [] # 設為空代表自動偵測，不限制 Bundle ID
    },
    # 未來要加新 App，只需複製上面的 {} 區塊貼在下面
]

# 4. 執行更新與雜湊計算
print(f"🚀 開始從 GitHub 抓取專案資料...")
# 加入 github_token 確保下載 IPA 計算 Hash 時不會被 GitHub 阻擋
srcmgr = AltSourceManager(src, apps_to_track, github_token=GITHUB_TOKEN)

try:
    srcmgr.update()
    
    if not srcmgr.src.get("apps"):
        print("❌ 錯誤：Parser 沒有找到任何有效的 App。請檢查 GitHub 是否有發布 IPA。")
    else:
        print(f"✅ 成功找到 {len(srcmgr.src['apps'])} 個項目！")
        print("正在計算檔案 Hash (這需要 1-2 分鐘)...")
        srcmgr.update_hashes() 
        srcmgr.save(prettify=True)
        print(f"🎉 更新完成！檔案已儲存至 {FILENAME}")
        
except Exception as e:
    print(f"❌ 執行出錯: {e}")
