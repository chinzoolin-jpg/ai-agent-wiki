from pathlib import Path
import json, html, re, zipfile, datetime, shutil
ROOT=Path('/mnt/data/ai_agent_hw')
(RAW:=ROOT/'raw').mkdir(exist_ok=True)
(WIKI:=ROOT/'wiki').mkdir(exist_ok=True)
(CONS:=WIKI/'concepts').mkdir(exist_ok=True)

sources=[
{'id':'S1','org':'OpenAI','title':'A practical guide to building agents','url':'https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/','notes':['實務上常把 agent 看成模型、工具和清楚的指令一起運作','工具可能拿來找資料，也可能拿來執行操作','單一 agent 就能用迴圈跑到完成條件，不是每個任務都要多 agent'], 'concepts':['C1','C2','C3','C4','C7']},
{'id':'S2','org':'Anthropic','title':'Building effective AI agents','url':'https://www.anthropic.com/research/building-effective-agents','notes':['分清楚事先排好順序的 workflow，和會自行選步驟的 agent','增強型 LLM 可以結合 retrieval、tools、memory','複雜任務可反覆利用工具回傳結果來修正下一步，也要有終止條件'], 'concepts':['C1','C2','C4','C6','C7']},
{'id':'S3','org':'Google Cloud','title':'What are AI agents?','url':'https://cloud.google.com/discover/what-are-ai-agents','notes':['AI agent 是圍繞目標，能理解任務並配合工具完成事情的系統','相關元件可能包含模型、記憶及工具','例子有客服、資料分析、程式協助等，也存在可靠性與倫理等問題'], 'concepts':['C1','C3','C5','C6']},
{'id':'S4','org':'Microsoft Learn','title':'Introduction to AI Agents','url':'https://learn.microsoft.com/en-us/startups/build/ai/agents/intro-agents','notes':['基本元件可整理為 LLM、Instructions、Tools','AI agent 會根據目標做規劃，也能透過工具取得資訊或採取行動','不等於每個聊天程式都會幫使用者真正執行事情'], 'concepts':['C1','C2','C3']},
{'id':'S5','org':'AWS','title':'AgentCore harness','url':'https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html','notes':['agent 運作時有 orchestration loop：模型、選工具、把結果送回模型','還要處理上下文、工具失敗和執行環境','正式系統需要安全、可觀測性等額外設計'], 'concepts':['C4','C6']},
{'id':'S6','org':'LangChain','title':'Thinking in the Graph API','url':'https://docs.langchain.com/oss/javascript/langgraph/thinking-in-graph-api','notes':['一個 graph 可以拆成 nodes、edges、shared state','有些 edge 固定，有些會依照結果決定下一個節點','網路或暫時性的失敗適合 retry，資料不足應回到補充資料節點'], 'concepts':['C7','C6']},
]
concepts=[
{'id':'C1','slug':'agent','title':'AI Agent 到底是什麼','sources':['S1','S3','S4'],'body':['簡單講就是幫忙做任務的 AI。不只跟人聊天，還能決定下一步要做什麼，必要時去用工具。','它通常會先看目標，過程中找資料、處理結果，再判斷事情做完沒。不是每個程式都能隨便操作電腦，還是要看它被開放什麼工具。']},
{'id':'C2','slug':'chatbot','title':'跟一般聊天機器人差在哪','sources':['S1','S2','S4'],'body':['一般問答型聊天機器人大多是問一句，回一句。','Agent 的重點不是名字，而是它能不能照目標走好幾步，用工具、看工具回來的資料，必要時再做下一步。','有些聊天產品本來就可以使用工具，所以這裡是方便理解的比較，不是絕對的分類。']},
{'id':'C3','slug':'parts','title':'大概需要什麼零件','sources':['S1','S3','S4'],'body':['模型 LLM：看懂問題，幫忙想下一步。','指令 Instructions：告訴 AI 要做什麼、哪些事不能做。','工具 Tools：像查資料、讀檔、呼叫服務。沒有開放工具的功能，不能假裝已經做了。','有些系統會加上記憶或知識庫，但不是每一種 Agent 都一定有這些。']},
{'id':'C4','slug':'loop','title':'Agent 會一直重複的步驟','sources':['S1','S2','S5'],'body':['接到任務 → 決定下一步 → 如果需要就使用工具 → 看工具回傳什麼 → 再決定下一步。','如果沒有完成就繼續跑，完成了就結束。遇到不能處理或需要權限的事情，也要停下來問人。','這個反覆檢查結果的過程，就是我們常講的 loop。']},
{'id':'C5','slug':'example','title':'生活例子：幫忙整理一日遊','sources':['S3','S1'],'body':['假設你要安排一日遊。一般聊天 AI 可能先給你一份建議。','如果是有相關權限和工具的 Agent，它可以查地點、找營業時間、比較移動距離，再排成一份行程。','這只是示範可能的流程，不代表這份作業真的幫人訂位，真實資料還是要查證。']},
{'id':'C6','slug':'risk','title':'Agent 也會出錯','sources':['S2','S3','S5','S6'],'body':['資料本身可能錯，工具也會失敗，結果不一定可靠。','像付款、寄信、刪除檔案等可能造成影響的操作，最好先得到人的同意。','如果一直卡在同一步，可以限制重試次數；來源不夠時回到找資料，不要硬編出答案。']},
{'id':'C7','slug':'graph','title':'Workflow 和 Graph','sources':['S2','S6','S1'],'body':['Workflow 是做事的順序。Graph 就是把各個步驟畫成節點，再用箭頭連起來。','例如資料夠不夠？夠就往下做；不夠就回去查。','本作業用的 graph 是：找資料 → 整理 Wiki → 查 Wiki → 做簡報 → 檢查；檢查沒過就回到前面修改。']},
]

def esc(x):return html.escape(str(x),quote=True)
def srclinks(ids, fmt='html'):
    if fmt=='html': return ' '.join(f'<a class="tag" href="AI_Agent_Wiki.html#source-{sid.lower()}">{sid}</a>' for sid in ids)
    return ', '.join(ids)

# schema and raw ingest notes
(ROOT/'AGENTS.md').write_text('''# 我的 LLM Wiki 規則

這次先討論題目和讀者，再去查資料，最後才做 Wiki 和 HTML 簡報。

資料分三層：
- raw/：六個來源的來源網址、讀取後的筆記。這不是把整個網頁原文複製回來。
- wiki/：用來源編號整理的知識頁，可以互相連結。
- 輸出 HTML：依照 wiki 的知識做簡報。每張教學頁有對應的 Wiki 編號。

Ingest：每看完一個來源，把網址和摘要存 raw，再更新 wiki。
Query：要做投影片時先查 wiki/index.md 和相關概念，不從印象硬寫。
Lint：檢查來源存在、概念對得到、簡報對得到、HTML 導覽有動。
問題沒過就回 source/概念整理改，不是只改投影片上的幾個字。
''',encoding='utf-8')
(ROOT/'00_先討論主題.txt').write_text('''先決定的事情

題目：AI Agent 是什麼
想給誰看：完全不懂的人，像一般同學
內容先回答幾個問題：是什麼？跟聊天 AI 差在哪？怎麼做事？可能出什麼錯？
不要一下就講很難的 API 或演算法。
資料來源：先找官方的解說或技術文章，至少五個。
確定來源跟內容後才整理 Wiki，最後從 Wiki 做簡報。
''',encoding='utf-8')
for s in sources:
    lines=[f"# {s['id']} {s['org']} - {s['title']}",f"原網址：{s['url']}","讀取日期：2026-11-21","資料種類：官方網站內容讀後整理成原始筆記（不是網頁全文）",'','這篇整理到的重點：']
    lines += [f'- {x}' for x in s['notes']]
    lines += ['', '可以用到的 Wiki 章節：'+', '.join(s['concepts']),'','出處請看上面網址。這邊只記重點，避免大段複製原文。']
    (RAW/f"{s['id'].lower()}_{s['org'].lower().replace(' ','_')}.md").write_text('\n'.join(lines)+'\n',encoding='utf-8')
index=['# AI Agent Wiki 目錄','', '這是一份從 6 個官方來源的讀後筆記整理出的 LLM Wiki。','']
for c in concepts:
    lines=[f"# {c['id']} {c['title']}",'',f"來源：{', '.join(c['sources'])}",'']+c['body']+['','相關章節：']
    for other in concepts:
        if other['id']!=c['id'] and set(other['sources']) & set(c['sources']) and len(lines)<12:
            lines.append(f"- [{other['id']} {other['title']}]({other['slug']}.md)")
    (CONS/f"{c['slug']}.md").write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
    index.append(f"- [{c['id']} {c['title']}](concepts/{c['slug']}.md) 來源：{', '.join(c['sources'])}")
index += ['', '## 六份來源','']+[f"- {s['id']} {s['title']}  {s['url']}" for s in sources]
(WIKI/'index.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
(WIKI/'overview.md').write_text('''# AI Agent 小整理

這個 Wiki 的意思不是把文章全部貼起來。是把來源先做筆記，再整理成自己的概念頁。

重要內容：
- C1 定義
- C2 chatbot 對比
- C3 模型、指令、工具
- C4 重複運作的 loop
- C5 生活例子
- C6 可能出錯
- C7 什麼是 graph

製作簡報時從這些頁取重點，並在每張簡報留下對應章節 ID。
''',encoding='utf-8')

# data layer loaded into both UI files (instead of relying on fetch file://)
data={'topic':'AI Agent 是什麼','read_at':'2026-11-21','sources':sources,'concepts':concepts}
(ROOT/'wiki_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

common_css='''
:root{--ink:#15243a;--muted:#536175;--bg:#f5f8fc;--line:#dfe7ee;--blue:#2368db;--lite:#eaf2ff;--mint:#d8f6ed;--warm:#fff0ce}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,"Noto Sans TC",Arial,sans-serif;color:var(--ink);background:var(--bg)}a{color:#1559b7}button,input{font:inherit}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #ffab39;outline-offset:3px}
.pill,.tag{display:inline-block;border:1px solid #bdd6fd;color:#235cbb;background:#eaf2ff;border-radius:12px;padding:3px 8px;font-size:12px;font-weight:700;text-decoration:none;margin:2px}
.small{color:var(--muted);font-size:14px}.topnav{display:flex;gap:14px;align-items:center;justify-content:space-between;padding:14px 24px;max-width:1200px;margin:auto}.topnav a{text-decoration:none;color:var(--ink)}.topnav strong{color:#1454a8}
'''

# Standalone wiki viewer
csections=[]
for c in concepts:
    p=''.join(f'<p>{esc(q)}</p>' for q in c['body'])
    ids=' '.join(f'<a class="tag" href="#source-{z.lower()}">{z}</a>' for z in c['sources'])
    csections.append(f'<article class="entry" id="concept-{c["id"].lower()}" data-search="{esc(c["title"]+" "+" ".join(c["body"]))}"><div class="eyebrow">{c["id"]} / 概念頁</div><h2>{esc(c["title"])}</h2>{p}<div class="small">我整理這頁時看了：{ids}</div></article>')
ss=[]
for s in sources:
    ss.append(f'<article class="source" id="source-{s["id"].lower()}"><b>{s["id"]} {esc(s["org"])}</b><h3>{esc(s["title"])}</h3><p class="small">來源整理筆記，點進去才是原官方文章</p><ul>{"".join(f"<li>{esc(t)}</li>" for t in s["notes"])}</ul><p>用到的概念：'+ ' '.join(f'<a class="tag" href="#concept-{x.lower()}">{x}</a>' for x in s['concepts'])+f'</p><a target="_blank" rel="noopener noreferrer" href="{esc(s["url"])}">看原本的文章 ↗</a></article>')
wiki_css='''
header.hero{max-width:1200px;margin:0 auto;padding:34px 24px 22px}.hero h1{font-size:clamp(34px,5vw,56px);margin:10px 0}.hero p{font-size:18px;line-height:1.6;max-width:720px;color:var(--muted)}.layout{max-width:1200px;margin:auto;display:grid;grid-template-columns:240px minmax(0,1fr);gap:25px;padding:0 24px 70px}.sidebar{position:sticky;top:20px;align-self:start;background:white;border:1px solid var(--line);border-radius:18px;padding:18px}.sidebar h3{margin:0 0 10px}.sidebar a{display:block;margin:10px 0;font-size:14px;text-decoration:none;color:#1d528b}.entry,.source{background:white;border:1px solid var(--line);border-radius:20px;padding:24px 28px;margin-bottom:20px;scroll-margin-top:18px;box-shadow:0 5px 20px #173f6510}.entry h2{font-size:27px;margin:5px 0 18px}.entry p{font-size:17px;line-height:1.9}.eyebrow{font-weight:800;color:#4676bc;font-size:13px;letter-spacing:1px}.sources{display:grid;grid-template-columns:repeat(2, minmax(0,1fr));gap:14px}.source{padding:20px;margin:0}.source h3{font-size:17px;margin:8px 0}.source ul{line-height:1.65;padding-left:22px}.searchbox{width:100%;padding:13px 16px;border-radius:14px;border:1px solid var(--line);background:white;margin-bottom:18px}.minihero{padding:18px 25px;background:#dceaff;border-radius:20px;margin:20px 0}.minihero a{font-weight:700}.hide{display:none!important}@media(max-width:750px){.layout{display:block}.sidebar{position:static;margin-bottom:20px}.sources{grid-template-columns:1fr}}
'''
wiki_html=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>我的 AI Agent Wiki</title><style>{common_css}{wiki_css}</style></head><body><nav class="topnav"><strong>AI AGENT / 我的 Wiki</strong><a href="AI_Agent_簡報.html">去看教學簡報 →</a></nav><header class="hero"><span class="pill">6 份官方資料讀後整理</span><span class="pill">7 個概念</span><h1>AI Agent 是什麼</h1><p>我想先搞懂它到底是什麼，跟聊天 AI 差多少。這裡先放查到的資料，整理好才拿去做簡報。</p></header><main class="layout"><aside class="sidebar"><h3>看哪一段</h3><a href="#concepts">概念整理</a>{''.join(f'<a href="#concept-{c["id"].lower()}">{c["id"]} {esc(c["title"])}</a>' for c in concepts)}<a href="#all-sources">六份資料</a><a href="#graph">我做 Wiki 的步驟</a></aside><div><input id="wikiSearch" class="searchbox" type="search" placeholder="可以搜尋，例如 工具、loop、出錯" aria-label="搜尋 Wiki 內容"><div class="minihero" id="graph"><b>我的作業流程</b><p>先看資料 → 整理 Wiki → 查 Wiki → 做簡報 → 檢查有沒有寫錯。不夠就回去找資料。</p><a href="AI_Agent_簡報.html">直接開簡報</a></div><div id="concepts">{''.join(csections)}</div><h2 id="all-sources">資料是從這 6 篇來的</h2><p class="small">S1～S6 都有網址和我自己的筆記，也有標對應的 Wiki 章節。</p><div class="sources">{''.join(ss)}</div></div></main><script>
const search = document.getElementById('wikiSearch'); search.addEventListener('input',()=>{{ const q=search.value.trim().toLowerCase();document.querySelectorAll('.entry').forEach(el=>{{el.classList.toggle('hide',!el.getAttribute('data-search').toLowerCase().includes(q) && !el.textContent.toLowerCase().includes(q))}})}});
</script></body></html>'''
(ROOT/'AI_Agent_Wiki.html').write_text(wiki_html,encoding='utf-8')

# Content is drawn from the seven wiki concept pages. All non-title slides have wiki refs.
slides=[
('今天來聊 AI Agent','先不用知道很難的技術名詞，我們從平常生活講起。','<div class="bigemoji">🤖</div><p class="lead">AI Agent 到底是不是比較厲害的聊天機器人？</p>',['C1']),
('先想一個例子','我有一件事想請 AI 幫忙','<div class="scenario">我想安排週末一日遊，但我不想自己一直找資料。</div><p>光回答我景點名稱，和真的幫我整理一份可以照著走的行程，感覺就不太一樣。</p>',['C5']),
('Agent 是什麼','一句話先記這個就好','<div class="huge">它是會照著目標<br>一步一步做事的 AI</div><p>它可能需要查資料、用工具，然後看做得怎樣，再做下一步。</p>',['C1']),
('跟一般聊天 AI 差在哪','不是說聊天 AI 一定做不到','<div class="compare"><div><h3>一般問答</h3><p>你問問題</p><p class="arrow">↓</p><p>它回答你</p></div><div><h3>Agent 做任務</h3><p>收到目標</p><p class="arrow">↓</p><p>找資料、用工具</p><p class="arrow">↓</p><p>看結果再繼續</p></div></div><p class="note">這是方便理解的比較，實際上有些聊天 AI 也有 Agent 功能。</p>',['C2']),
('Agent 大概有三個東西','沒有想像中複雜','<div class="three"><div><span>🧠</span><h3>模型</h3><p>理解問題和決定下一步</p></div><div><span>📋</span><h3>指令</h3><p>告訴它任務和限制</p></div><div><span>🧰</span><h3>工具</h3><p>查資料或執行操作</p></div></div>',['C3']),
('它其實會一直繞一圈','這個循環叫做 loop','<div class="flowline"><span>接到目標</span><b>→</b><span>決定下一步</span><b>→</b><span>使用工具</span><b>→</b><span>看看結果</span></div><div class="loopback">↖ 沒做完就再想一次，完成才停 ↙</div><p class="note">工具回來的資訊可能不夠，所以需要再查，不是每次只做一步。</p>',['C4']),
('再回去看一日遊的例子','假設它真的有查詢工具','<ol class="steps"><li>先看看有哪些景點</li><li>查營業時間和交通資料</li><li>看看順不順路，不合理就改</li><li>最後才整理行程給我</li></ol><p class="note">這是示意圖，沒有真的去訂位或買票。</p>',['C5','C4']),
('為什麼這次要先做 Wiki','不能只靠 AI 自己亂說','<div class="flowline"><span>讀 6 份資料</span><b>→</b><span>整理 Wiki</span><b>→</b><span>從 Wiki 找重點</span><b>→</b><span>做投影片</span></div><p>每一頁我都有標 Wiki 概念編號。這樣寫錯的時候可以回頭找到來源。</p>',['C7','C1']),
('也不是完全不會出錯','不能因為有 Agent 就什麼都信','<div class="three"><div><span>❓</span><h3>資料錯</h3><p>查到舊的時間或錯的內容</p></div><div><span>🔌</span><h3>工具壞</h3><p>查不到資料就要停下來</p></div><div><span>🔒</span><h3>權限</h3><p>付款、刪資料等要先確認</p></div></div>',['C6']),
('小小測驗','先自己想一下','<div class="quiz"><p><b>問題 1</b> Agent 一定每次只回答一句就結束嗎？</p><button class="reveal">點我看答案</button><p class="answer">不一定，它可能需要使用工具、檢查結果，然後繼續下一步。</p><hr><p><b>問題 2</b> AI 說已經訂好位，就代表真的訂好了嗎？</p><button class="reveal">點我看答案</button><p class="answer">不行。要看它有沒有真的用到工具，還要確認實際回傳結果。</p></div>',['C4','C6']),
('今天記住這幾件事就好','沒有要一次記很多','<div class="summary"><p>① Agent 是要完成目標，不只是講話。</p><p>② 它可能用工具，而且會一直看結果。</p><p>③ 工具和資料都有可能錯，所以還是要檢查。</p></div>',['C1','C3','C4','C6']),
('我參考了哪些資料','這些都可以回 Wiki 找到','<div class="credit">'+''.join(f'<p><b>{s["id"]} {esc(s["org"])}</b>　{esc(s["title"])}</p>' for s in sources)+'</div><p>如果想看原網站，直接開 Wiki 裡的來源清單就有網址。</p>',['C1','C7']),
]

slides_css='''
html,body{height:100%;overflow:hidden}body{background:#edf2fa}body::before{content:"";position:fixed;inset:0;background:radial-gradient(circle at 87% 10%,#d5e6ff,transparent 40%),radial-gradient(circle at 2% 90%,#dbf9eb,transparent 34%);pointer-events:none}
.deck{height:100%;max-width:1180px;margin:0 auto;display:flex;flex-direction:column;position:relative;padding:10px 20px 16px}.slidewrap{flex:1;min-height:0;display:flex}.slide{flex:1;min-height:0;overflow-y:auto;background:#fff;border:1px solid #d4e1ee;border-radius:25px;box-shadow:0 18px 48px #163e661a;padding:clamp(25px,5vw,70px) clamp(25px,6vw,90px);display:flex;flex-direction:column;justify-content:center;position:relative;margin-top:8px}.js .slide{display:none}.js .slide.active{display:flex}.slide:before{content:"";position:absolute;left:0;top:30px;bottom:30px;width:7px;border-radius:8px;background:#387ddd}.slide h1{font-size:clamp(28px,4vw,54px);line-height:1.25;letter-spacing:-.025em;margin:0 0 14px}.subtitle{font-size:clamp(18px,2vw,24px);color:#516782;margin:0 0 24px}.slide p,.slide li{font-size:clamp(17px,1.8vw,24px);line-height:1.65}.slide .lead{font-size:clamp(22px,2.5vw,31px);font-weight:700;text-align:center}.bigemoji{font-size:clamp(80px,10vw,140px);text-align:center}.huge{font-size:clamp(27px,3.5vw,48px);text-align:center;background:#e8f2ff;padding:40px;border-radius:20px;font-weight:800;line-height:1.45}.scenario{padding:30px;background:#e7f3ff;border-radius:22px;font-size:clamp(23px,2.8vw,34px);font-weight:700}.compare,.three{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}.compare>div,.three>div{background:#f2f7ff;border:1px solid #dce8f8;border-radius:20px;padding:26px;text-align:center}.compare h3,.three h3{font-size:27px;margin:4px}.compare .arrow{line-height:.8;color:#3a7fd2}.three{grid-template-columns:repeat(3,1fr)}.three span{font-size:53px}.three p{font-size:20px}.flowline{display:flex;align-items:center;gap:11px;justify-content:center;flex-wrap:wrap}.flowline span{display:inline-flex;align-items:center;justify-content:center;background:#e7f2ff;border:1px solid #cce0fa;border-radius:14px;padding:22px 15px;min-height:100px;font-size:clamp(18px,1.8vw,22px);font-weight:700;text-align:center}.flowline b{font-size:28px;color:#4c82c4}.loopback{text-align:center;color:#227355;margin:22px 0;font-size:25px;font-weight:800}.note{color:#627388!important;font-size:16px!important;margin-top:22px}.steps{padding:12px 0 10px 42px}.steps li{padding:12px 0;font-weight:600}.quiz{background:#f7fbff;padding:20px 35px;border-radius:19px}.quiz button{background:#235ec0;color:white;border:0;border-radius:10px;padding:10px 15px;cursor:pointer}.quiz .answer{display:none;color:#176449;font-weight:700}.quiz .answer.show{display:block}.quiz hr{border:0;border-top:1px solid #d9e5ef;margin:25px 0}.summary{background:#eef6ff;border-radius:20px;padding:18px 34px}.summary p{font-size:clamp(20px,2.3vw,28px);font-weight:700}.credit{font-size:15px}.credit p{font-size:17px;margin:9px 0}.controls{display:flex;align-items:center;gap:12px;justify-content:space-between;padding:14px 2px}.controls button{border:0;border-radius:13px;padding:12px 20px;background:#1d5dbc;color:white;font-weight:700;cursor:pointer}.controls button:disabled{opacity:.35;cursor:default}.counter{font-size:14px;color:#4d617b}.progress{height:6px;background:#dbe5f3;border-radius:99px;overflow:hidden;flex:1;max-width:350px}.bar{height:100%;width:0;background:#2478d7;transition:width .15s}.wikiref{position:absolute;right:34px;bottom:18px;font-size:12px;color:#59708a}.wikiref a{display:inline-block;margin-left:5px;text-decoration:none;color:#235cb0}.hint{font-size:12px;color:#627a96}.noprint{display:flex}@media(max-width:700px){html,body{overflow:auto;min-height:100%}.slide{padding:30px 25px;min-height:70vh}.compare,.three{grid-template-columns:1fr}.flowline span{min-height:60px;padding:12px}.wikiref{position:static;margin-top:20px}.controls{gap:7px}.controls button{padding:10px}.hint{display:none}}@media print{html,body{height:auto;overflow:visible;background:white}.deck{display:block;padding:0;max-width:none}.slidewrap{display:block}.slide,.js .slide{display:flex!important;height:180mm;break-after:page;margin:0;border:0;box-shadow:none;border-radius:0;overflow:hidden}.controls,.topnav{display:none!important}}
'''
items=[]
for i,(title,sub,content,refs) in enumerate(slides):
    # title slide intentionally still receives source anchors for traceability
    cited=' '.join(f'<a href="AI_Agent_Wiki.html#concept-{r.lower()}" target="_blank" rel="noopener">{r}</a>' for r in refs)
    items.append(f'<section class="slide" data-page="{i+1}" data-wiki="{",".join(refs)}" aria-label="第 {i+1} 張：{esc(title)}"><h1>{esc(title)}</h1><p class="subtitle">{esc(sub)}</p><div>{content}</div><div class="wikiref">Wiki 對應：{cited}</div></section>')
slideshow=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Agent 是什麼｜教學 HTML 簡報</title><style>{common_css}{slides_css}</style><script>document.documentElement.classList.add('js')</script></head><body><div class="deck"><nav class="topnav"><strong>我的教學簡報</strong><a href="AI_Agent_Wiki.html" target="_blank" rel="noopener">查看來源 Wiki</a></nav><main class="slidewrap">{''.join(items)}</main><footer class="controls noprint"><button id="prev" aria-label="上一張">← 上一張</button><span class="counter" id="counter" aria-live="polite"></span><div class="progress" role="progressbar" aria-label="簡報進度" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="bar" id="bar"></div></div><span class="hint">← → 可以換頁</span><button id="next" aria-label="下一張">下一張 →</button></footer></div><script>
const pages=[...document.querySelectorAll('.slide')];let pos=0;function render(){{pages.forEach((p,i)=>p.classList.toggle('active',i===pos));document.querySelector('#prev').disabled=pos===0;document.querySelector('#next').disabled=pos===pages.length-1;document.querySelector('#counter').textContent=`${{pos+1}} / ${{pages.length}}`;const pct=Math.round((pos+1)/pages.length*100);document.querySelector('#bar').style.width=pct+'%';document.querySelector('.progress').setAttribute('aria-valuenow',pct);location.hash='p'+(pos+1)}}
function go(d){{pos=Math.max(0,Math.min(pages.length-1,pos+d));render()}}document.querySelector('#prev').addEventListener('click',()=>go(-1));document.querySelector('#next').addEventListener('click',()=>go(1));document.addEventListener('keydown',(e)=>{{if(e.target.matches('input,textarea'))return;if(['ArrowRight',' ','PageDown'].includes(e.key)){{e.preventDefault();go(1)}} if(['ArrowLeft','PageUp'].includes(e.key)){{e.preventDefault();go(-1)}}}});document.querySelectorAll('.reveal').forEach(b=>b.addEventListener('click',()=>{{const p=b.nextElementSibling;p.classList.toggle('show');b.textContent=p.classList.contains('show')?'收起答案':'點我看答案'}}));const m=location.hash.match(/^#p(\\d+)$/);if(m)pos=Math.min(pages.length-1,Math.max(0,parseInt(m[1],10)-1));render();
</script></body></html>'''
(ROOT/'AI_Agent_簡報.html').write_text(slideshow,encoding='utf-8')

(ROOT/'workflow.md').write_text('''# 我這次的流程圖

```mermaid
flowchart TD
 A[選主題，先想要教誰] --> B[找官方資料]
 B --> C[做 raw 來源筆記]
 C --> D[整理成 Wiki 7 個概念]
 D --> E{來源有沒有對得上?}
 E -- 沒有 --> B
 E -- 有 --> F[查 Wiki 做簡報大綱]
 F --> G[產生 HTML 簡報]
 G --> H{內容和網頁測試有沒有過?}
 H -- 內容錯 --> D
 H -- HTML壞了 --> G
 H -- OK --> I[完成]
```

會重複的地方：缺資料回去找，概念對不起來源回 Wiki 改，按鈕或版面壞掉回 HTML 改。

為什麼要這樣：如果只在簡報表面修字，真正的 Wiki 可能還是錯的。先把來源和概念修好比較不容易一直犯同樣錯。
''',encoding='utf-8')

# simple submission (casual, no overly formal presentation)
submission='''# AI Agent 是什麼

## 1 我做的 Wiki
這次我選 AI Agent。因為之前只知道它好像就是 AI 會幫忙做事，但也沒很清楚它到底跟一般聊天 AI 有什麼差別。所以我就先找一些資料看，主要想弄懂它是什麼、需要什麼東西、怎麼一直做下去。

一開始先決定我想給完全沒接觸過的人看，所以不要寫太難。然後才找資料，這樣比較知道要找什麼。

## 2 Wiki 成果
我整理了 6 份資料，是 OpenAI、Anthropic、Google Cloud、Microsoft Learn、AWS、LangChain 的文章或文件。先放到 raw 筆記，再整理成 7 個概念頁。像是 Agent 定義、工具、loop 還有出錯的問題。

Wiki 檔：AI_Agent_Wiki.html
整包裡還有 wiki/index.md、concepts、raw 的六份來源筆記。

## 3 HTML 簡報
簡報叫 AI Agent 是什麼，總共 12 頁。先用一日遊舉例，再介紹 Agent 跟聊天 AI 差別，後面有 loop、風險跟小測驗。

簡報檔：AI_Agent_簡報.html
用瀏覽器打開就能按下一頁，鍵盤左右也可以。每張頁面下面有 Wiki 的 C 編號，可以連回去看。

## 4 我的流程
先想題目要講什麼 → 找 6 份資料 → 整理原始筆記 → 做 Wiki → 從 Wiki 找出要講的東西 → 做簡報 → 再檢查。

如果整理時發現資料不夠，就回去找。假如簡報的內容沒有對到 Wiki，就先回 Wiki 檢查，不是直接亂補內容。網頁按鈕有問題的話才回去改 HTML。

## 5 一次執行跟檢查
我有先把 6 個來源整理進去，最後 Wiki 是 7 個概念，簡報 12 頁。

檢查主要是看有沒有少來源、簡報每頁能不能找到 Wiki 對應、連結會不會連錯。還有 HTML 的上一頁下一頁和小測驗按鈕。詳細結果在 check_log.txt。

## 6 我後來有改什麼
我覺得最容易弄錯的是把查到的資料直接濃縮成簡報那個地方，因為很容易太簡短，變成講得太肯定。像是講一般聊天 AI 和 Agent 的差別，很容易寫成聊天 AI 完全不能用工具，但其實不能這樣說。

所以我把檢查往前移到整理 Wiki 的時候，就先看原本的來源是不是有這樣講，也把那句改成只是方便理解的比較。然後才做 HTML。這樣簡報如果有問題，也知道要回哪一頁 Wiki 找原因。

整體做完發現，多花一個檢查 Wiki 的步驟比較好，不然如果投影片已經做好才發現內容怪怪的，還要一頁一頁修。

---
交作業前提醒：把你的學校、學號、系級、姓名加進標題。如果老師要可公開點的網址，還需要把兩個 HTML 上傳到網頁空間，現在這份是本機可開的成果檔。
'''
(ROOT/'作業繳交說明_口語版.txt').write_text(submission,encoding='utf-8')
print('wrote',len(sources),'source notes',len(concepts),'wiki pages',len(slides),'slides')
