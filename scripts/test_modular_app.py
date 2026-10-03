# -*- coding: utf-8 -*-
"""
Playwright automated test script for SMS Exam Prep Web App
Tests 4-tab top-level navigation, recruit sub-tabs, EMT-1 sub-tabs, and checklist.
"""
import os
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright

def run_tests():
    html_path = os.path.abspath("index.html")
    url = f"file:///{html_path.replace(os.sep, '/')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Capture console errors
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("console", lambda msg: print(f"[{msg.type}] {msg.text}") if msg.type == 'error' else None)

        print(f"Navigating to {url}...")
        page.goto(url)
        page.wait_for_timeout(1000)

        # 1. Test Home Tab
        print("Checking Home tab...")
        assert page.is_visible("#tab-home-content"), "Home tab should be visible by default"
        home_text = page.inner_text("#home-content-body")
        assert "成功嶺替代役新訓" in home_text, "Home should contain main title"
        assert "專案緣起與初衷" in home_text, "Home should contain project origin section"
        assert "網站核心四大功能模組導覽" in home_text, "Home should contain module cards"
        assert "四階段滿分備考路線圖" in home_text, "Home should contain roadmap"
        print("[OK] Home tab verified!")

        # 2. Test switching to Recruit Training
        print("Checking Recruit tab...")
        page.click("button[data-tab='recruit']")
        page.wait_for_timeout(500)
        assert page.is_visible("#tab-recruit-content"), "Recruit tab should be visible"
        assert not page.is_visible("#tab-home-content"), "Home tab should be hidden"
        
        # Verify Recruit Sub-tabs
        recruit_subtabs = page.query_selector_all(".recruit-subtab-btn")
        assert len(recruit_subtabs) == 6, f"Expected 6 recruit subtabs, got {len(recruit_subtabs)}"
        
        # Test Recruit Bank Subtab
        print("Checking Recruit Bank subtab...")
        page.click("button[data-subtab='bank']")
        page.wait_for_timeout(500)
        assert page.is_visible("#recruit-sub-bank"), "Bank subtab view should be visible"
        bank_count = page.inner_text("#bank-filtered-count")
        print(f"Recruit bank question count: {bank_count}")
        assert int(bank_count) >= 270, f"Expected ~272 questions, got {bank_count}"

        # Test Recruit Regulations Subtab
        print("Checking Recruit Regulations subtab...")
        page.click("button[data-subtab='regulations']")
        page.wait_for_timeout(500)
        assert page.is_visible("#recruit-sub-regulations"), "Regulations subtab should be visible"
        reg_text = page.inner_text("#regulations-content-body")
        assert "替代役實施條例" in reg_text, "Regulations content should load"

        # 3. Test switching to EMT-1
        print("Checking EMT-1 tab...")
        page.click("button[data-tab='emt']")
        page.wait_for_timeout(500)
        assert page.is_visible("#tab-emt-content"), "EMT tab should be visible"
        assert not page.is_visible("#tab-recruit-content"), "Recruit tab should be hidden"

        # Test EMT Study subtab (Legal Articles Alignment)
        print("Checking EMT Study & Legal Alignment...")
        page.click("button[onclick*=\"switchEmtSubTab('study')\"]")
        page.wait_for_timeout(500)
        emt_study_text = page.inner_text("#emt-subtab-container")
        assert "緊急醫療救護法" in emt_study_text, "EMT study should contain Emergency Medical Services Act"
        assert "救護技術員管理辦法" in emt_study_text, "EMT study should contain EMT Regulations"
        assert "善良撒瑪利亞人條款" in emt_study_text, "EMT study should contain Good Samaritan Clause"
        assert "全國法規資料庫" in emt_study_text, "EMT study should contain MOJ links"
        print("[OK] EMT Legal Alignment verified!")

        # Test EMT Bank subtab
        print("Checking EMT Bank subtab...")
        page.click("button[onclick*=\"switchEmtSubTab('bank')\"]")
        page.wait_for_timeout(500)
        emt_bank_text = page.inner_text("#emt-subtab-container")
        assert "96" in emt_bank_text, "EMT bank should show 96 questions"
        print("[OK] EMT Bank verified!")

        # 4. Test Checklist Tab
        print("Checking Checklist tab...")
        page.click("button[data-tab='checklist']")
        page.wait_for_timeout(500)
        assert page.is_visible("#tab-checklist-content"), "Checklist tab should be visible"
        checklist_text = page.inner_text("#checklist-content-body")
        assert "新訓用品" in checklist_text or "檢核表" in checklist_text, "Checklist should load properly"
        print("[OK] Checklist tab verified!")

        # 5. Check Console Errors
        if errors:
            print(f"[FAIL] Found page errors: {errors}")
            browser.close()
            sys.exit(1)
        else:
            print("[OK] Zero JavaScript errors!")

        browser.close()
        print("[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
