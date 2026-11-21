from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading, functools
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re, json, subprocess
root=Path('/mnt/data/ai_agent_hw')
w=root/'AI_Agent_Wiki.html'; s=root/'AI_Agent_簡報.html'
source_files=list((root/'raw').glob('*.md'))
concept_files=list((root/'wiki/concepts').glob('*.md'))
wdom=BeautifulSoup(w.read_text(encoding='utf-8'),'html.parser')
sdom=BeautifulSoup(s.read_text(encoding='utf-8'),'html.parser')
items=sdom.select('section.slide')
checks=[]
checks.append(('至少5份來源筆記',len(source_files)>=5, f'{len(source_files)}份'))
checks.append(('Wiki概念頁數',len(concept_files)==7, f'{len(concept_files)}頁'))
checks.append(('簡報張數',len(items)>=8, f'{len(items)}張'))
concepts={x.get('id') for x in wdom.select('article.entry')}
sources={x.get('id') for x in wdom.select('article.source')}
checks.append(('來源筆記與HTML來源都有',len(sources)==len(source_files),f'{len(sources)}項'))
missing=[]
for page in items:
    for link in page.select('.wikiref a'):
        if link.get('href','').split('#')[-1] not in concepts:missing.append((page.get('data-page'),link.get('href')))
checks.append(('投影片都有Wiki對應而且連得上',not missing and all(p.select('.wikiref a') for p in items), '缺漏='+str(missing)))
missing2=[]
for concept in wdom.select('article.entry'):
    for link in concept.select('.tag'):
        if link.get('href','')[1:] not in sources:missing2.append(link.get('href'))
checks.append(('Wiki概念有對到來源S編號',not missing2 and all(x.select('.tag') for x in wdom.select('article.entry')),'缺漏='+str(missing2)))
js=sdom.select('script')[-1].get_text()
tmp=root/'_check.js';tmp.write_text(js)
node=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True)
checks.append(('簡報JS語法檢查',node.returncode==0,(node.stderr or 'ok').strip()))
tmp.unlink()
# local HTTP avoids file:// restrictions in automated browser
handler=functools.partial(SimpleHTTPRequestHandler,directory=str(root))
server=ThreadingHTTPServer(('127.0.0.1',0), handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base=f'http://127.0.0.1:{server.server_port}'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':800},device_scale_factor=1)
    console_errors=[];page.on('pageerror',lambda e:console_errors.append(str(e)))
    page.set_content(s.read_text(encoding='utf-8'),wait_until='load');page.wait_for_timeout(200)
    checks.append(('HTML起始頁顯示',page.locator('.slide.active').count()==1 and page.locator('#counter').inner_text()=='1 / 12',page.locator('#counter').inner_text()))
    page.locator('#next').click();checks.append(('下一張按鈕',page.locator('#counter').inner_text()=='2 / 12',page.locator('#counter').inner_text()))
    page.keyboard.press('ArrowRight');checks.append(('鍵盤右鍵',page.locator('#counter').inner_text()=='3 / 12',page.locator('#counter').inner_text()))
    page.locator('#prev').click();checks.append(('上一張按鈕',page.locator('#counter').inner_text()=='2 / 12',page.locator('#counter').inner_text()))
    for i in range(8): page.locator('#next').click()
    checks.append(('小測驗頁導覽',page.locator('.slide.active h1').inner_text()=='小小測驗',page.locator('.slide.active h1').inner_text()))
    page.locator('.slide.active .reveal').first.click()
    checks.append(('小測驗答案顯示',page.locator('.slide.active .answer').first.is_visible(),'show' if page.locator('.slide.active .answer').first.is_visible() else 'not visible'))
    page.screenshot(path=str(root/'_slide_screenshot.png'))
    page.set_content(w.read_text(encoding='utf-8'),wait_until='load');page.wait_for_timeout(150)
    checks.append(('Wiki有6份來源',page.locator('article.source').count()==6,str(page.locator('article.source').count())))
    page.locator('#wikiSearch').fill('工具')
    vis=page.locator('article.entry:not(.hide)').count()
    checks.append(('Wiki搜尋可用',0<vis<7,f'工具搜尋有{vis}筆'))
    page.screenshot(path=str(root/'_wiki_screenshot.png'),full_page=False)
    checks.append(('瀏覽器沒有腳本錯誤',not console_errors,str(console_errors)))
    browser.close()
server.shutdown()
print('\n'.join(('PASS' if passed else 'FAIL')+' '+name+': '+details for name,passed,details in checks))
(root/'check_log.txt').write_text('2026-11-21 一次實際執行測試\n\n'+'\n'.join(('通過' if passed else '未通過')+' '+name+'：'+details for name,passed,details in checks)+'\n',encoding='utf-8')
print('passed',sum(x[1] for x in checks),'/',len(checks))
