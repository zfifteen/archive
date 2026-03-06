from playwright.sync_api import sync_playwright

url = "https://grok.com/share/bGVnYWN5_27d78b14-8aa8-4f16-86e1-1a6784bb7eda"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, timeout=10000)  # 10 second timeout
    content = page.text_content('html')
    print(content)
    browser.close()