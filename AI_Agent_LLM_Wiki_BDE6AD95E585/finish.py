from pathlib import Path
import zipfile
R=Path('/mnt/data/ai_agent_hw')
log=R/'check_log.txt'
log.write_text(log.read_text(encoding='utf-8')+'''\n這次實際遇到的錯誤：\n第一次跑瀏覽器互動檢查時，先點了下一頁按鈕，再按鍵盤右鍵，頁數沒有照預期前進。\n原因是 JS 原本連按鈕聚焦時的方向鍵也跳過。\n修法：只略過輸入框、文字區的鍵盤事件，讓方向鍵在按過按鈕後仍可切頁。\n第二次重新測，以上16項都通過。\n\n另一個內容檢查提醒：\n原本在整理概念時很容易把聊天室和Agent分成完全不能重疊的兩種。\n查看 S1、S2、S4 後，Wiki C2 使用比較保守的說法，指出有些聊天程式也有Agent功能。\n這裡是對來源的內容檢查，不是宣稱實際做了一個自動跑AI的Agent。\n\n測試方式：用 Chromium 執行HTML內容及JS互動（自動化測試環境不允許file://直接導航，所以以頁面內容載入），並用BeautifulSoup檢查來源和錨點。\n''',encoding='utf-8')
(R/'wiki'/'log.md').write_text('''# Wiki 操作紀錄

## 2026-11-21 先決定主題
題目選 AI Agent 是什麼，受眾是沒學過這類東西的人。

## 2026-11-21 ingest
從 6 篇官方資料的頁面讀取後，建立 6 份 raw/ 來源筆記。不是把原網頁全文照貼。

## 2026-11-21 compile
將內容整理成 C1-C7 七個 Wiki 概念頁，並在每頁標 S1-S6 出處。

## 2026-11-21 query
從 Wiki C1-C7 選出基本定義、比較、零件、loop、案例、風險等重點，產生 12 張投影片。每頁下方有 Wiki 編號。

## 2026-11-21 lint 第一次
內容溯源有通過，但 HTML 簡報的鍵盤右鍵在按鈕聚焦的時候沒反應。

## 2026-11-21 修正與 lint 第二次
修正鍵盤處理，16/16 項檢查通過。細節可看 check_log.txt。
''',encoding='utf-8')
sub=R/'作業繳交說明_口語版.txt'
t=sub.read_text(encoding='utf-8')
t=t.replace('我覺得最容易弄錯的是把查到的資料直接濃縮成簡報那個地方，因為很容易太簡短，變成講得太肯定。像是講一般聊天 AI 和 Agent 的差別，很容易寫成聊天 AI 完全不能用工具，但其實不能這樣說。\n\n所以我把檢查往前移到整理 Wiki 的時候，就先看原本的來源是不是有這樣講，也把那句改成只是方便理解的比較。然後才做 HTML。這樣簡報如果有問題，也知道要回哪一頁 Wiki 找原因。\n\n整體做完發現，多花一個檢查 Wiki 的步驟比較好，不然如果投影片已經做好才發現內容怪怪的，還要一頁一頁修。',
'''這次實際測的時候，出錯的是 HTML 切頁的地方。就是按了下一頁後再按鍵盤右鍵，結果沒有換頁。後來發現是程式把按鈕聚焦時的按鍵跳過了，所以改了一下，後來重新測就正常了。\n\n所以我把操作檢查往前移，HTML 一產生出來就先測上一頁、下一頁和鍵盤，不要到最後全部做好才測。\n\n另外內容整理也很容易講得太肯定，例如不能說聊天 AI 一定不能用工具。所以我在做 Wiki 時就先對來源，不要等簡報已經寫好才去改。\n\n我覺得流程真的要留回去改的箭頭，不然發現錯了就很麻煩。''')
t=t.replace('詳情結果在 check_log.txt。','詳情結果在 check_log.txt。')
sub.write_text(t,encoding='utf-8')

index='''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AI Agent 作業成果</title><style>*{box-sizing:border-box}body{font-family:system-ui,"Noto Sans TC",sans-serif;background:#f3f7fc;color:#192b44;margin:0}.wrap{max-width:900px;margin:8vh auto;padding:24px}h1{font-size:clamp(32px,5vw,52px);margin:12px 0}p{font-size:18px;line-height:1.7}.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;margin-top:30px}.card{display:block;color:#1e3b67;text-decoration:none;background:white;border:1px solid #dce7f3;border-radius:20px;padding:24px;box-shadow:0 8px 25px #233d5815}.card h2{margin:7px 0}.card:hover{border-color:#3f86df;transform:translateY(-2px)}.tag{color:#2774c9;font-weight:800}.flow{margin-top:30px;padding:22px;background:#e0eefe;border-radius:16px}.flow strong{display:block;margin-bottom:8px}footer{margin-top:30px;font-size:14px;color:#62718a}@media(max-width:700px){.cards{grid-template-columns:1fr}}</style></head><body><div class="wrap"><div class="tag">LLM WIKI + HTML SLIDES</div><h1>AI Agent 是什麼</h1><p>這次我先讀 6 份資料整理 Wiki，再從 Wiki 做一份給初學者看的教學簡報。下面可以直接打開。</p><div class="cards"><a class="card" href="AI_Agent_Wiki.html"><div>📚</div><h2>我的 AI Agent Wiki</h2><p>6 個來源，7 個概念，可以搜尋內容。</p></a><a class="card" href="AI_Agent_簡報.html"><div>🖥️</div><h2>HTML 教學簡報</h2><p>12 頁，可以按按鈕換頁，也有一個小測驗。</p></a></div><div class="flow"><strong>我這次的流程</strong>先找資料 → 整理 raw 筆記 → 整理 Wiki → 從 Wiki 查重點 → 做簡報 → 檢查。<p>如果內容沒有對到來源，就回 Wiki 修改。如果網頁切頁有問題，就回 HTML 修改。</p></div><footer>這是可以直接開的本機版 HTML，還沒有自動發布到公開網站。</footer></div></body></html>'''
(R/'index.html').write_text(index,encoding='utf-8')
(R/'README_上傳網址說明.txt').write_text('''怎麼用\n\n1 解壓縮整包，先雙擊 index.html，就能選 Wiki 或簡報。\n2 兩個 HTML 請放在同一個資料夾，這樣頁面之間的相對連結才不會壞。\n3 作業繳交說明_口語版.txt 可直接拿去改成自己的版本，補學校、學號、系級和姓名。\n\n如果老師要求真正的網路連結\n這份目前是本機 HTML，不是已經上傳完成的網站。可建立一個 GitHub repository，把 index.html、AI_Agent_Wiki.html、AI_Agent_簡報.html 放在同一層，開 GitHub Pages。公開後把 Pages 的實際網址貼到作業中。\n不要直接把 sandbox 檔案連結當成永久公開網址。\n\n備註\nraw/ 六份是讀官方文章後的來源筆記，並非原始網站全文抓取。\nwiki/ 有 Wiki 的索引和 7 個概念頁。\nAGENTS.md 說明 ingest / query / lint 流程。\ncheck_log.txt 有實際的檢查和修正紀錄。\n''',encoding='utf-8')
# remove temp screenshots and scripts from final package, but retain the actual reproducible QA code
for name in ('_slide_screenshot.png','_wiki_screenshot.png'):
    p=R/name
    if p.exists():p.unlink()
zip_path=Path('/mnt/data/AI_Agent_LLM_Wiki_作業整包.zip')
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(R.rglob('*')):
        if p.is_file() and not p.name.startswith('_') and not p.name.endswith('.pyc'):
            z.write(p,p.relative_to(R))
print('zip size',zip_path.stat().st_size,'files',len(zipfile.ZipFile(zip_path).namelist()))
