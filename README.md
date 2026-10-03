# 成功嶺替代役新訓備考（SMS Exam Prep）

替代役基礎訓練學科與 EMT-1 的題庫練習網站，附法規全文與入營用品清單。

- 線上版：<https://lee200202.github.io/SMS-Exam-Prep/>
- 這是役男自行整理的非官方資料。題目來自歷屆役男分享，內容如與主管機關公告不同，以公告為準。

## 網站內容

| 區塊 | 內容 | 連結 |
| --- | --- | --- |
| 新訓學科 | 模擬考（50 題、40 分鐘、60 分及格）、快速練習、章節練習、錯題重測、題庫查詢 | `#quiz`、`#bank` |
| 新訓重點 | 替代役實施條例、志願服務法、權益服勤、射擊 | `#regulations`、`#volunteer`、`#rights`、`#shooting` |
| EMT-1 | 模擬考（50 題、50 分鐘、70 分及格）、練習、題庫、重點整理、學習資源 | `#emt`、`#emt-bank`、`#emt-study`、`#emt-resources` |
| 法規全文 | 17 部法規的現行條文，可搜尋 | `#laws`、`#emt-laws` |
| 用品清單 | 可勾選的入營物品、管制說明、不用帶的物品、經驗提醒 | `#checklist` |

題數、章節數等數字都由資料計算，畫面與文件不寫死。目前資料：新訓 272 題（是非 154、選擇 118），EMT-1 96 題。

## 資料來源與查核狀態

- **法規全文**：`scripts/fetch_laws.py` 直接從[全國法規資料庫](https://law.moj.gov.tw/)下載並解析，不經人工改寫。每部法規的修正日期與取得日期顯示在「法規全文」頁。
- **題庫**：歷屆役男分享的考古題。與現行法規牴觸的題目已依現行條文改寫，並在題目上標示「已依現行法規改寫」與改寫原因；現行法規已無對應規定的題目標為「舊法題」，不列入測驗。
- **重點整理、用品清單、成績配分、薪給**：屬於歷屆經驗整理，頁面上都有標示，實際以當梯次通知與主管機關公告為準。

查核紀錄見 [docs/資料查核紀錄.md](docs/資料查核紀錄.md)。

## 作答規則

- 未作答的題目不計分，也**不會**加入錯題本。結果頁分開顯示答對、答錯、未作答。
- 模擬考交卷後才判定對錯，錯題以交卷時的最終答案為準。練習模式每題作答後立即鎖定並顯示解析。
- 選項會隨機排列，正解跟著選項走；含「以上皆是」這類選項的題目不打亂。
- 模擬考以實際時間計時。離開測驗頁或重新整理會自動暫停，回到測驗頁可繼續；時間到自動交卷。
- 錯題本、收藏、未完成的測驗與清單勾選只存在瀏覽器的 localStorage，首頁可以一鍵清除。

## 專案結構

```
index.html            頁面骨架
css/style.css         樣式（手寫，無 CSS 框架）
js/app.js             主程式（無外部相依）
data/*.json           題庫、講義、法規資料（原始資料）
data/data_bundle.js   由 JSON 產生的資料包（首頁載入）
data/laws_bundle.js   法規全文資料包（進入法規頁才載入）
pdf/                  三份可列印的 PDF
scripts/              資料下載、檢查、打包、PDF 產生與瀏覽器測試
```

網站是純靜態檔案，沒有後端也沒有外部 CDN，可直接部署在 GitHub Pages，或雙擊 `index.html` 開啟。

## 修改資料後要做的事

```bash
python scripts/fetch_laws.py            # 需要更新法規條文時
python scripts/validate_data.py         # 檢查題庫結構、來源與資料包一致性
python scripts/generate_bundle.py       # 重新產生資料包
python scripts/generate_pdf_bank.py     # 新訓題庫 PDF
python scripts/generate_emt_pdf.py      # EMT-1 題庫 PDF
python scripts/generate_checklist_pdf.py  # 用品清單 PDF
python scripts/test_app.py              # 瀏覽器回歸測試（需要 playwright）
```

`scripts/test_app.py` 後面加網址可以直接測線上版，例如
`python scripts/test_app.py https://lee200202.github.io/SMS-Exam-Prep/`。

`scripts/` 內其餘 `update_*`、`merge_*`、`build_*` 等是早期整理資料用的一次性腳本，重跑會覆蓋目前已校對的 JSON，請不要再執行。

## 授權與聲明

題庫與筆記整理自公開分享的役男資料，法規條文取自全國法規資料庫，僅供備考與教育用途。
