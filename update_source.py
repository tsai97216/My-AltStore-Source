import os
import json
from altparse import AltSourceManager, Parser, altsource_from_file

# === 基礎設定區 ===
FILENAME = "apps.json" 
YOUR_GITHUB_USERNAME = "tsai97216" 
SOURCE_NAME = "Tsai 的私人商店" 

# 1. 確保基礎 JSON 檔案存在，防止讀取失敗
if not os.path.exists(FILENAME):
    initial_source = {
        "name": SOURCE_NAME,
        "identifier": f"com.{YOUR_GITHUB_USERNAME}.custom.source",
        "apps": []
    }
    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(initial_source, f, indent=2, ensure_ascii=False)

# 2. 載入現有資料庫
src = altsource_from_file(FILENAME)

# 3. 定義你要自動追蹤的 App 列表
# 未來想增加新 App，只需在下面增加一個字典區塊 {}
apps_to_track = [
    {
        "parser": Parser.GITHUB,
        "kwargs": {
            "repo_author": "bggRGjQaUbCoE",
            "repo_name": "PiliPlus",
            "prefer_date": True,
        },
        # 重要修正：設為空列表 []，代表自動抓取 Release 裡所有的 IPA，不進行 ID 過濾
        "ids": [] 
    },
]

# 4. 執行更新與雜湊計算
print(f"🚀 正在檢查更新並同步 GitHub Releases...")
srcmgr = AltSourceManager(src, apps_to_track)

try:
    # 抓取最新版本資訊
    srcmgr.update()
    
    # 自動下載 IPA 並計算 SHA-1 Hash 值 (這是 AltStore 安裝成功的關鍵)
    # 注意：如果檔案較大，這步在 GitHub Actions 執行時可能需要 1-2 分鐘
    srcmgr.update_hashes() 
    
    # 將結果美化並儲存到 apps.json
    srcmgr.save(prettify=True)
    print(f"✅ 更新完成！檔案已儲存至 {FILENAME}")
    
except Exception as e:
    print(f"❌ 發生錯誤: {e}")
