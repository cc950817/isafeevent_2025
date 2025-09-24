# 2025年數位素養自動答題腳本

### 答案選擇策略

- **兩頁測驗格式**：完整處理從第一頁到第二頁的所有題目
- **第一頁**：16題李克特量表（自我評量）
  - 選項：非常同意、同意、普通、不同意、非常不同意
  - **統一選擇「普通」**（不使用 AI，節省 API 呼叫）
- **第二頁**：16題選擇題（情境應用題目）
  - 每題4個選項
  - **使用 AI 智能分析**並選擇最合適的答案

## 📦 安裝需求

### Gemini 版本

```bash
pip install selenium webdriver-manager google-generativeai
```

### OpenAI 版本

```bash
pip install -r requirements_openai.txt
```

或手動安裝：

```bash
pip install selenium webdriver-manager openai
```

## 使用方法

### Gemini 版本

```bash
python bot_gemini.py
```

### OpenAI 版本

```bash
python bot_openai.py
```

### 共同步驟

1. 等待瀏覽器開啟並手動登入網站
2. 登入完成後按 Enter 繼續
3. 輸入對應的 API 金鑰：
   - Gemini: Google AI Studio API Key
   - OpenAI: OpenAI API Key
4. 設定答題次數和間隔時間
5. 腳本將自動完成兩頁測驗

## 🚀 快速開始

1. **選擇版本**：根據需求選擇 Gemini 或 OpenAI 版本
2. **安裝相依套件**：使用對應的安裝指令
3. **取得 API 金鑰**：按照上述步驟申請
4. **執行腳本**：使用 `python bot_xxx.py` 指令
5. **開始答題**：按照提示完成設定即可自動答題
