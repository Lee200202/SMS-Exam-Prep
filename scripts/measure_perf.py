# -*- coding: utf-8 -*-
"""
效能與對比量測（Playwright + Chromium）。結果寫入 docs/效能量測_<日期>.md。

用法：python scripts/measure_perf.py https://lee200202.github.io/SMS-Exam-Prep/

- 每個情境冷快取跑 3 次取中位數，另跑 1 次暖快取。
- 「4G 中階手機」是模擬值：下載 4 Mbps、上傳 3 Mbps、延遲 150 ms、CPU 降速 4 倍，390x844 視窗。
  這是實驗室量測，不代表所有使用者的實際速度。
- 對比依 WCAG 2.2 的公式，從 css/style.css 的色彩變數計算。
"""
import datetime
import os
import re
import statistics
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = {
    "桌機（不限速）": {"viewport": {"width": 1440, "height": 900}, "net": None, "cpu": 1},
    "4G 中階手機（模擬）": {"viewport": {"width": 390, "height": 844},
                     "net": {"offline": False, "latency": 150, "downloadThroughput": 4_000_000 / 8, "uploadThroughput": 3_000_000 / 8},
                     "cpu": 4},
}
OBSERVE = """
window.__lcp = 0; window.__cls = 0;
new PerformanceObserver((list) => { for (const e of list.getEntries()) window.__lcp = e.startTime; })
  .observe({ type: 'largest-contentful-paint', buffered: true });
new PerformanceObserver((list) => { for (const e of list.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
  .observe({ type: 'layout-shift', buffered: true });
"""
COLLECT = """() => {
  const nav = performance.getEntriesByType('navigation')[0];
  const res = performance.getEntriesByType('resource');
  return { lcp: window.__lcp, cls: window.__cls, dcl: nav.domContentLoadedEventEnd,
           bytes: nav.transferSize + res.reduce((n, r) => n + r.transferSize, 0), requests: res.length + 1 };
}"""


def measure(browser, base, profile, warm=False):
    ctx = browser.new_context(viewport=profile["viewport"])
    page = ctx.new_page()
    page.add_init_script(OBSERVE)
    cdp = ctx.new_cdp_session(page)
    if warm:
        page.goto(base + "#home")
        page.wait_for_selector("#home-stats")
    if profile["net"]:
        cdp.send("Network.enable")
        cdp.send("Network.emulateNetworkConditions", profile["net"])
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": profile["cpu"]})
    failed = []
    page.on("requestfailed", lambda r: failed.append(r.url))
    page.goto(base + "#home")
    page.wait_for_selector("#home-stats")
    page.wait_for_timeout(1200)
    data = page.evaluate(COLLECT)

    # 互動延遲：題庫搜尋（輸入到結果更新）、法規搜尋（含首次載入該分組全部法規）
    page.goto(base + "#bank")
    page.wait_for_selector("#bank-list .qcard")
    data["bank_search"] = page.evaluate("""async () => {
      const input = document.querySelector('#bank-search'); const t = performance.now();
      input.value = '撫卹'; input.dispatchEvent(new Event('input', { bubbles: true }));
      while (!document.querySelector('#bank-list mark')) await new Promise(r => setTimeout(r, 10));
      return performance.now() - t; }""")
    page.goto(base + "#emt-laws")
    page.wait_for_selector("#law-list details")
    data["law_search"] = page.evaluate("""async () => {
      const input = document.querySelector('#law-search'); const t = performance.now();
      input.value = '救護車'; input.dispatchEvent(new Event('input', { bubbles: true }));
      while (!document.querySelector('#law-list mark')) await new Promise(r => setTimeout(r, 20));
      return performance.now() - t; }""")
    data["failed"] = len(failed)
    ctx.close()
    return data


def luminance(hex_color):
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def contrast_rows():
    css = open(os.path.join(ROOT, "css", "style.css"), encoding="utf-8").read()
    light = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6});", css[css.index(":root {"):css.index(':root[data-theme="dark"]')]))
    dark = dict(light)
    dark.update(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6});", css[css.index(':root[data-theme="dark"]'):css.index("*, *::before")]))
    pairs = [("text", "bg", "正文／頁面底色"), ("text", "surface", "正文／卡片"), ("muted", "surface", "次要文字／卡片"),
             ("muted", "bg", "次要文字／頁面底色"), ("primary", "surface", "連結／卡片"), ("on-primary", "primary", "主要按鈕文字"),
             ("red", "red-soft", "錯誤文字／錯誤底色"), ("ok", "ok-soft", "正確文字／正確底色"),
             ("amber", "amber-soft", "提醒文字／提醒底色"), ("header-text", "header-bg", "頁首文字")]
    rows = []
    for theme, tokens in (("淺色", light), ("深色", dark)):
        for fg, bg, label in pairs:
            ratio = contrast(tokens[fg], tokens[bg])
            rows.append((theme, label, tokens[fg], tokens[bg], ratio, "通過" if ratio >= 4.5 else "未達 4.5"))
    return rows


def main():
    base = (sys.argv[1] if len(sys.argv) > 1 else "https://lee200202.github.io/SMS-Exam-Prep/").rstrip("/") + "/"
    today = datetime.date.today().isoformat()
    out = ["# 效能與對比量測", "", "量測日：%s　對象：%s" % (today, base), "",
           "Playwright Chromium 實驗室量測。4G 與中階手機是模擬條件（4 Mbps／150 ms／CPU 降速 4 倍），不代表所有使用者的實際速度。",
           "INP 需要真實使用者互動資料，這裡改列兩個代表性互動的完成時間。", "",
           "## 首頁載入與互動", "",
           "| 情境 | 快取 | LCP (ms) | DOMContentLoaded (ms) | CLS | 傳輸量 (KB) | 請求數 | 題庫搜尋 (ms) | 法規搜尋含首次載入 (ms) | 失敗請求 |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    raw = ["", "## 原始數據", ""]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, profile in PROFILES.items():
            cold = [measure(browser, base, profile) for _ in range(3)]
            warm = measure(browser, base, profile, warm=True)
            med = {k: statistics.median(run[k] for run in cold) for k in cold[0]}
            for label, d in (("冷（3 次中位數）", med), ("暖（1 次）", warm)):
                out.append("| %s | %s | %.0f | %.0f | %.3f | %.0f | %d | %.0f | %.0f | %d |" % (
                    name, label, d["lcp"], d["dcl"], d["cls"], d["bytes"] / 1024, d["requests"],
                    d["bank_search"], d["law_search"], d["failed"]))
            raw.append("- %s 冷快取三次：%s" % (name, [{k: round(v, 3) for k, v in run.items()} for run in cold]))
            raw.append("- %s 暖快取：%s" % (name, {k: round(v, 3) for k, v in warm.items()}))
            print(name, "LCP 中位數 %.0f ms" % med["lcp"])
        browser.close()
    out += raw
    out += ["", "## 色彩對比（WCAG 2.2 AA，一般文字需 4.5:1）", "",
            "| 外觀 | 組合 | 前景 | 背景 | 對比 | 結果 |", "| --- | --- | --- | --- | --- | --- |"]
    out += ["| %s | %s | %s | %s | %.2f | %s |" % row for row in contrast_rows()]
    path = os.path.join(ROOT, "docs", "效能量測_%s.md" % today)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("已寫入", path)


if __name__ == "__main__":
    main()
