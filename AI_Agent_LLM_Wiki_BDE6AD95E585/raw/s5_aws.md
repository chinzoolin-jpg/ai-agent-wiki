# S5 AWS - AgentCore harness
原網址：https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html
讀取日期：2026-11-21
資料種類：官方網站內容讀後整理成原始筆記（不是網頁全文）

這篇整理到的重點：
- agent 運作時有 orchestration loop：模型、選工具、把結果送回模型
- 還要處理上下文、工具失敗和執行環境
- 正式系統需要安全、可觀測性等額外設計

可以用到的 Wiki 章節：C4, C6

出處請看上面網址。這邊只記重點，避免大段複製原文。
