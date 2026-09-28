import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel='chrome',
        headless=False,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        viewport={'width': 1280, 'height': 800}
    )
    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("Navigating to Dcard...", flush=True)
    page.goto('https://www.dcard.tw/f/military/p/262186096', wait_until='commit')
    page.wait_for_timeout(6000)

    js = """
    async () => {
        const r1 = await fetch('/service/api/v3/posts/262186096/comments?sort=oldest&limit=100&withPreview=true&excludeKeywords=false&disableBlockingList=false&lang=zh-TW');
        const mainData = await r1.json();
        const mainComments = mainData.items || [];
        
        const allComments = [];
        
        for (const c of mainComments) {
            allComments.push({
                type: 'root',
                floor: c.floor,
                id: c.id,
                school: c.school,
                content: c.content,
                subCommentCount: c.subCommentCount
            });
            
            if (c.subCommentCount > 0) {
                try {
                    const subRes = await fetch(`/service/api/v3/posts/262186096/comments?parentId=${c.id}`);
                    const subData = await subRes.json();
                    const subItems = subData.items || [];
                    for (const sc of subItems) {
                        allComments.push({
                            type: 'sub',
                            parentFloor: c.floor,
                            parentId: c.id,
                            floor: sc.floor,
                            id: sc.id,
                            school: sc.school,
                            content: sc.content
                        });
                    }
                } catch(err) {
                    allComments.push({
                        type: 'error',
                        parentId: c.id,
                        error: err.toString()
                    });
                }
            }
        }
        return allComments;
    }
    """
    all_comments = page.evaluate(js)
    with open('data/all_dcard_comments.json', 'w', encoding='utf-8') as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=2)

    print(f"Successfully fetched {len(all_comments)} total comments and subcomments!", flush=True)
    browser.close()
