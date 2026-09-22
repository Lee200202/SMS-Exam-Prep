import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/export?format=html'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        print(f"Downloaded HTML, size: {len(html)}")
        matches = re.findall(r'<h[1-6][^>]*id="([^"]*)"[^>]*>(.*?)</h[1-6]>', html, re.DOTALL)
        for hid, htext in matches:
            clean = re.sub(r'<[^>]*>', '', htext).strip()
            if '36ei31r' in hid:
                print(f"MATCH TARGET: {hid} -> {clean}")
        print("\nFirst 20 headings:")
        for hid, htext in matches[:20]:
            clean = re.sub(r'<[^>]*>', '', htext).strip()
            print(f"{hid} -> {clean[:50]}")
except Exception as e:
    print('Error:', e)
