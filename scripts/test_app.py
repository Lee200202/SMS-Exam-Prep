# -*- coding: utf-8 -*-
"""
瀏覽器端回歸測試（Playwright）。會在本機起一個靜態伺服器後實際操作網站。

用法：
  python scripts/test_app.py                 # 測本機檔案
  python scripts/test_app.py https://lee200202.github.io/SMS-Exam-Prep/   # 測線上版
"""
import functools
import http.server
import json
import os
import sys
import threading

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTES = ["home", "quiz", "bank", "regulations", "volunteer", "rights", "shooting", "laws",
          "emt", "emt-bank", "emt-study", "emt-laws", "emt-resources", "checklist"]
MISTAKES = "JSON.parse(localStorage.getItem('sms_mistakes'))"
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(("  通過  " if ok else "  失敗  ") + name + (("｜" + str(detail)) if detail != "" and not ok else ""))


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(Quiet, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, "http://127.0.0.1:%d/" % server.server_address[1]


def load_json(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def session(page, bank):
    return page.evaluate("b => JSON.parse(localStorage.getItem('sms_session_v2_' + b))", bank)


def correct_index(question):
    if question["type"] == "true_false":
        return 0 if question["answer"] == "O" else 1
    return question["answer"]


def run(base):
    recruit = {q["id"]: q for q in load_json("questions.json")["questions"]}
    emt = {q["id"]: q for q in load_json("emt_questions.json")["questions"]}
    tf = sum(q["type"] == "true_false" for q in recruit.values())

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        errors, external = [], []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("request", lambda r: external.append(r.url) if not r.url.startswith((base, "data:")) else None)

        def go(route):
            page.goto(base + "#" + route)
            page.wait_for_selector("#app > *")

        def click_answer(bank_name, bank, right=True):
            s = session(page, bank_name)
            q = bank[s["items"][s["current"]]["id"]]
            idx = correct_index(q)
            if not right:
                idx = (idx + 1) % (2 if q["type"] == "true_false" else len(q["options"]))
            page.click('.option[data-opt="%d"]' % idx)
            return q

        def submit():
            page.click('.quiz-bar [data-action="quiz-submit"]')
            page.click('#dialog [data-dialog="1"]')
            page.wait_for_selector("#result-title")

        def result_numbers():
            return [page.inner_text(s) for s in ("#result-correct", "#result-wrong", "#result-blank")]

        print("首頁與路由")
        go("home")
        stats = page.inner_text("#home-stats")
        check("首頁題數由資料計算", all(str(n) in stats for n in (len(recruit), tf, len(recruit) - tf, len(emt))), stats)
        for route in ROUTES:
            go(route)
            check("深連結 #%s 可開啟" % route, page.locator("#app h1, #app h2").count() > 0)
        go("recruit")
        check("舊連結 #recruit 轉到測驗", page.locator('[data-action="quiz-start"]').count() == 4)

        print("快速練習：未作答不算錯")
        page.evaluate("localStorage.clear()")
        page.reload()
        page.click('[data-mode="quick"]')
        click_answer("recruit", recruit, right=False)
        check("答錯後立即顯示解析區", page.locator("#feedback.is-bad").count() == 1)
        submit()
        check("結果分開顯示答對/答錯/未答", result_numbers() == ["0", "1", "19"], result_numbers())
        check("只有答錯的 1 題進錯題本", len(page.evaluate(MISTAKES)) == 1, page.evaluate(MISTAKES))

        print("選項洗牌後正解不變")
        page.click('[data-action="result-close"]')
        page.click('[data-mode="quick"]')
        ok = True
        for i in range(20):
            click_answer("recruit", recruit, right=True)
            ok = ok and page.locator("#feedback.is-ok").count() == 1
            if i < 19:
                page.click('[data-action="quiz-next"]')
        check("20 題都選正解皆判定答對", ok)
        submit()
        check("全對得 100 分", page.inner_text(".score b") == "100")
        page.click('[data-action="result-close"]')

        print("模擬考：改答案、暫停、重新整理、交卷")
        page.evaluate("localStorage.clear()")
        page.reload()
        page.click('[data-mode="mock"]')
        first = click_answer("recruit", recruit, right=False)
        check("模擬考作答時不顯示對錯", page.locator("#feedback").count() == 0)
        click_answer("recruit", recruit, right=True)
        page.click('[data-action="quiz-next"]')
        click_answer("recruit", recruit, right=False)
        go("bank")
        check("離開測驗頁自動暫停", session(page, "recruit")["status"] == "paused")
        go("quiz")
        check("回到測驗頁顯示繼續作答", page.locator('[data-action="quiz-resume"]').count() == 1)
        page.reload()
        page.wait_for_selector('[data-action="quiz-resume"]')
        page.click('[data-action="quiz-resume"]')
        s = session(page, "recruit")
        check("重新整理後題目與答案保留", s["status"] == "active" and len(s["answers"]) == 2 and s["current"] == 1)
        check("計時器顯示剩餘時間", page.inner_text("#quiz-timer").startswith(("39:", "40:")))
        page.click('.quiz-bar [data-action="quiz-submit"]')
        check("交卷前提示未作答題數", "48 題沒有作答" in page.inner_text("#dialog-body"))
        page.click('#dialog [data-dialog="1"]')
        page.wait_for_selector("#result-title")
        check("模擬考結果 1 對 1 錯 48 未答", result_numbers() == ["1", "1", "48"], result_numbers())
        mistakes = page.evaluate(MISTAKES)
        check("改成正解的題目不進錯題本", first["id"] not in mistakes and len(mistakes) == 1, mistakes)

        print("時間到自動交卷")
        page.click('[data-action="result-close"]')
        page.click('[data-mode="mock"]')
        page.click('.quiz-bar [data-action="quiz-pause"]')
        page.evaluate("""() => { const k = 'sms_session_v2_recruit'; const s = JSON.parse(localStorage.getItem(k));
            s.elapsedMs = s.totalMs - 1500; localStorage.setItem(k, JSON.stringify(s)); }""")
        page.reload()
        page.click('[data-action="quiz-resume"]')
        page.wait_for_selector("#result-title", timeout=8000)
        check("倒數結束自動交卷並標示", "時間到" in page.inner_text("#app"))
        check("時間到的未答題不進錯題本", len(page.evaluate(MISTAKES)) == 1, page.evaluate(MISTAKES))

        print("錯題重測")
        page.click('[data-action="result-close"]')
        page.click('[data-mode="mistakes"]')
        click_answer("recruit", recruit, right=True)
        check("錯題重測答對後移出錯題本", page.evaluate(MISTAKES) == [])
        page.click('.quiz-bar [data-action="quiz-pause"]')
        page.click('[data-action="quiz-discard"]')
        page.click('#dialog [data-dialog="1"]')

        print("EMT-1 測驗")
        go("emt")
        check("EMT 及格標準顯示 70 分", "70 分及格" in page.inner_text("#app"))
        page.click('[data-mode="quick"]')
        ok = True
        for i in range(20):
            click_answer("emt", emt, right=True)
            ok = ok and page.locator("#feedback.is-ok").count() == 1
            if i < 19:
                page.click('[data-action="quiz-next"]')
        check("EMT 20 題選正解皆答對（含洗牌）", ok)
        page.click('.quiz-bar [data-action="quiz-pause"]')
        check("EMT 暫停後可繼續", page.locator('[data-action="quiz-resume"]').count() == 1)
        page.click('[data-action="quiz-discard"]')
        page.click('#dialog [data-dialog="1"]')
        check("放棄後不再顯示未完成測驗", page.locator('[data-action="quiz-resume"]').count() == 0)

        print("題庫搜尋與篩選")
        go("emt-bank")
        page.click("#bank-search")
        page.keyboard.type("GCS", delay=60)
        page.wait_for_timeout(400)
        check("連續輸入 GCS 不被截斷", page.input_value("#bank-search") == "GCS")
        check("輸入後焦點仍在搜尋框", page.evaluate("document.activeElement.id") == "bank-search")
        check("GCS 有搜尋結果並標示關鍵字", page.locator("#bank-list mark").count() > 0)
        page.fill("#bank-search", "止血")
        page.wait_for_timeout(300)
        check("中文關鍵字可搜尋", page.locator("#bank-list .qcard").count() > 0)
        page.fill("#bank-search", "zzzz不存在")
        page.wait_for_timeout(300)
        check("零結果顯示空狀態", page.locator("#bank-list .empty").count() == 1 and "找到 0 題" in page.inner_text("#bank-count"))
        page.click('#bank-list [data-action="bank-reset"]')
        check("清除篩選後回到全部題目", "找到 %d 題" % len(emt) in page.inner_text("#bank-count"))
        go("bank")
        page.select_option("#bank-type", "tf")
        check("題型篩選是非題", "找到 %d 題" % tf in page.inner_text("#bank-count"))
        page.select_option("#bank-type", "all")
        page.locator("#bank-list .qcard .star-btn").first.click()
        page.select_option("#bank-scope", "bookmarks")
        check("收藏後可在「我的收藏」找到", page.locator("#bank-list .qcard").count() == 1)
        page.select_option("#bank-scope", "all")
        page.check("#bank-hide")
        check("背題模式隱藏答案", page.locator("#bank-list .is-answer").count() == 0)
        page.locator('#bank-list [data-action="bank-reveal"]').first.click()
        check("可單題顯示答案", page.locator("#bank-list .is-answer").count() == 1)
        page.uncheck("#bank-hide")
        page.fill("#bank-search", "MC-037")
        page.wait_for_timeout(300)
        check("MC-037 正解為 10年", "10年" in page.inner_text("#bank-list .is-answer"))
        page.fill("#bank-search", "MC-053")
        page.wait_for_timeout(300)
        check("舊法題標示不列入測驗", "不列入測驗" in page.inner_text("#bank-list"))

        print("法規全文")
        go("laws")
        page.wait_for_selector("#law-list details")
        check("新訓法規 15 部", page.locator("#law-list details").count() == 15)
        page.locator("#law-list details summary").first.click()
        page.wait_for_selector("#law-list .law-article")
        check("展開後顯示條文", "第 38 條" in page.locator("#law-list details").first.inner_text())
        page.fill("#law-search", "十年不行使")
        page.wait_for_timeout(300)
        check("條文搜尋可找到第 38 條", "第 38 條" in page.inner_text("#law-list"))
        go("emt-laws")
        page.wait_for_selector("#law-list details")
        check("EMT 法規 2 部", page.locator("#law-list details").count() == 2)

        print("用品清單")
        go("checklist")
        pack = sum(len(c["items"]) for c in load_json("study_data.json")["packing_list"]["categories"] if c["kind"] == "pack")
        check("只有要準備的物品可勾選", page.locator("[data-check]").count() == pack)
        page.locator("[data-check]").first.check()
        check("勾選後進度更新", page.inner_text("#check-all").startswith("1 /"))
        page.reload()
        page.wait_for_selector("[data-check]")
        check("重新整理後勾選保留", page.inner_text("#check-all").startswith("1 /"))
        page.click('[data-action="check-reset"]')
        page.click('#dialog [data-dialog="1"]')
        check("清除勾選", page.inner_text("#check-all").startswith("0 /"))

        print("外觀、儲存與資源")
        page.click("#theme-toggle")
        theme = page.evaluate("document.documentElement.dataset.theme")
        page.reload()
        check("深淺模式切換後保留", page.evaluate("document.documentElement.dataset.theme") == theme)
        page.evaluate("""() => { ['sms_mistakes','sms_bookmarks','sms_checklist','sms_session_v2_recruit','sms_session_v2_emt']
            .forEach(k => localStorage.setItem(k, '{壞資料')); }""")
        go("home")
        page.reload()
        page.wait_for_selector("#app > *")
        check("localStorage 壞資料不影響載入", page.locator("#home-stats").count() == 1)
        for path in page.evaluate("Array.from(document.querySelectorAll('a[download]')).map(a => a.getAttribute('href'))"):
            check("PDF 可下載 …" + path[-16:], page.request.head(base + path).status == 200)
        check("沒有載入外部資源", not external, external[:3])

        print("手機版面")
        for width in (390, 360):
            mobile = browser.new_context(viewport={"width": width, "height": 780})
            m = mobile.new_page()
            wide = []
            for route in ROUTES:
                m.goto(base + "#" + route)
                m.wait_for_selector("#app > *")
                m.wait_for_timeout(150)
                if m.evaluate("document.documentElement.scrollWidth > window.innerWidth"):
                    wide.append(route)
            check("%dpx 各頁無水平捲動" % width, not wide, wide)
            m.goto(base + "#quiz")
            m.click('[data-mode="quick"]')
            small = m.evaluate("""Array.from(document.querySelectorAll('.option, .quiz .btn'))
                .filter(e => e.getBoundingClientRect().height < 44).length""")
            check("%dpx 作答按鈕高度至少 44px" % width, small == 0, small)
            font = m.evaluate("parseFloat(getComputedStyle(document.querySelector('.option')).fontSize)")
            check("%dpx 選項文字至少 16px" % width, font >= 16, font)
            mobile.close()

        check("全程沒有 JS 錯誤", not errors, errors[:3])
        browser.close()


if __name__ == "__main__":
    server = None
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip("/") + "/"
    else:
        server, base_url = serve()
    print("測試對象：", base_url)
    try:
        run(base_url)
    finally:
        if server:
            server.shutdown()
    failed = [n for n, ok in results if not ok]
    print("\n%d 項通過，%d 項失敗" % (len(results) - len(failed), len(failed)))
    sys.exit(1 if failed else 0)
