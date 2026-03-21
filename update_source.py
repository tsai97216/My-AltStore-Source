import os
import json
from altparse import AltSourceManager, Parser, altsource_from_file

# === 基礎設定區 ===
FILENAME = "apps.json" 
YOUR_GITHUB_USERNAME = "tsai97216" 
SOURCE_NAME = "Tsai 的私人商店" # 這是顯示在 AltStore 上的標題

# 1. 確保基礎 JSON 檔案存在
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
        },
        "ids": ["com.bgg.piliplus"] 
    },
    # 未來想加別的 GitHub 專案，就複製上面的 {} 區塊貼在下面
]

# 4. 執行更新與雜湊計算
print(f"🚀 正在檢查更新...")
srcmgr = AltSourceManager(src, apps_to_track)

try:
    srcmgr.update()
    # 自動下載 IPA 並計算 Hash 值，確保 AltStore 能正常安裝
    srcmgr.update_hashes() 
    srcmgr.save(prettify=True)
    print(f"✅ 更新完成！檔案已儲存至 {FILENAME}")
except Exception as e:
    print(f"❌ 發生錯誤: {e}")
