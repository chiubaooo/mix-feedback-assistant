# AI 混音修改意見智能提煉工廠 (Mix Feedback Assistant)

專為音樂工作室與 AI 混音外包接案設計的意見梳理與防禦守衛系統。

## 🎯 核心解決問題
1. **客戶習慣**：客戶愛用語音發布零散、情緒化或玄學的修改意見（如「人聲太小」、「不夠立體」、「大氣一點」）。
2. **智翔與客服痛點**：不用辛苦逐句聽打整理，只要在微信**長按語音「轉文字」**，複製貼進網頁。
3. **混音師解脫**：一秒生成結構化、對應軌道 (Vocal, Drums, Bass, Space) 的 Action Items 清單。
4. **防禦合約邊界**：內建修改版本計數器（v1~v3 預設微調、v4+ 進入 500~1000 計費預警），並自動生成帶有確認邊界的微信回覆文案。

## 🚀 啟動方式

### Windows 雙擊啟動
直接雙擊執行：
```bash
tools/mix_feedback_web/run_app.bat
```

### 命令列手動啟動
```bash
python -m streamlit run tools/mix_feedback_web/app.py
```
啟動後會自動在瀏覽器開啟 `http://localhost:8501`。

## ⚙️ 運作模式
1. **本機極速語意規則模式 (預設)**：
   - 零延遲、免任何 API Key、完全離線可用。
   - 自動將文字拆解並映射至 6 大關鍵音樂軌道分類。
2. **Gemini AI 深度模式 (選填)**：
   - 在側邊欄填入 Gemini API Key 即可開啟。
   - 自動將口語形容詞轉化為混音專業術語 (EQ/Compression/Reverb Decay)，並偵測是否有人聲重錄或推翻架構之風險預警。
