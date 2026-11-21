# S6 LangChain - Thinking in the Graph API
原網址：https://docs.langchain.com/oss/javascript/langgraph/thinking-in-graph-api
讀取日期：2026-11-21
資料種類：官方網站內容讀後整理成原始筆記（不是網頁全文）

這篇整理到的重點：
- 一個 graph 可以拆成 nodes、edges、shared state
- 有些 edge 固定，有些會依照結果決定下一個節點
- 網路或暫時性的失敗適合 retry，資料不足應回到補充資料節點

可以用到的 Wiki 章節：C7, C6

出處請看上面網址。這邊只記重點，避免大段複製原文。
