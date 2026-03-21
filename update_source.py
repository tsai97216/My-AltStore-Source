import os
import json
import logging
from altparse import AltSourceManager, Parser

# 開啟日誌模式，這樣我們在 Actions 裡可以看到更多細節
logging.basicConfig(level=logging.INFO)

FILENAME = "apps.json" 
YOUR_GITHUB_USERNAME = "tsai97216" 
SOURCE_NAME = "Tsai 的私人商店" 
# 確保從環境變數抓取 Token，如果抓不到也沒關係（會用匿名方式連線）
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# 1. 建立一個全新的、基礎的 Source 結構 (避免讀取舊檔失敗)
new_source = {
    "name": SOURCE_NAME,
    "identifier": f"com.{YOUR_GITHUB_USERNAME}.custom.source",
    "apps": []
}

# 2. 定義要抓取的清單
apps_to_track = [
    {
        "parser": Parser.GITHUB,
        "kwargs": {
            "repo_author": "bggRGjQaUbCoE",
            "repo_name": "PiliPlus",
            "prefer_date": True
        },
        "ids": [] # 改成空列表，不限制 ID
    }
]

print(f"🔍 正在連線至 GitHub 抓取專案: bggRGjQaUbCoE/PiliPlus...")

# 3. 初始化管理員，加入更強的錯誤捕捉
try:
    # 這裡我們不帶舊檔案，直接用 new_source 開始
    srcmgr = AltSourceManager(new_source, apps_to_track, github_token=GITHUB_TOKEN)
    
    # 執行更新，並手動檢查結果
    srcmgr.update()
    
    # 檢查抓到的結果是否為 None 或空
    apps_list = srcmgr.src.get("apps")
    if apps_list is None:
        print("❌ 錯誤：GitHub API 回傳了空結果 (None)。這可能是因為 API 被限速或 Token 失效。")
    elif len(apps_list) == 0:
        print("⚠️ 警告：成功連線但沒找到任何符合條件的 IPA 檔案。")
    else:
        print(f"✅ 成功找到 {len(apps_list)} 個項目！正在計算 Hash...")
        # 只有在有抓到 App 的情況下才計算 Hash
        srcmgr.update_hashes()
        
        # 強制寫入檔案
        with open(FILENAME, 'w', encoding='utf-8') as f:
            json.dump(srcmgr.src, f, indent=2, ensure_ascii=False)
        print(f"💾 更新成功！檔案已儲存至 {FILENAME}")

except Exception as e:
    # 捕捉具體的錯誤位置
    import traceback
    print(f"❌ 發生嚴重錯誤：\n{traceback.format_exc()}")
