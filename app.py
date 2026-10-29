"""
AI 混音修改意見智能提煉工廠 (Mix Feedback Assistant)
針對微信語音轉文字的口語碎念，自動提煉出：
1. 混音師內部執行清單 (Action Items)
2. 客戶確認覆盤話術 (Client Confirmation)
3. 修改版本與邊界守衛 (v1~v3 免費, v4+ 封頂預警)
"""

import os
import re
import json
import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI 混音修改意見提煉工廠",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Awwwards / Modern Dark Studio Vibe
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e222d 0%, #252b3b 100%);
        border: 1px solid #2e3648;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .tag-vocal { background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .tag-bass { background-color: #8b5cf6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .tag-drum { background-color: #ec4899; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .tag-space { background-color: #10b981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .stTextArea textarea {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.6;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Audio feedback parsing logic (Rule-based & AI-ready)
KEYWORDS_MAP = {
    "人聲/主唱 (Vocal)": ["人聲", "主唱", "唱歌", "聲音", "嘴型", "齒音", "太小聲", "大聲", "突兀", "悶", "乾", "濕", "靠前", "推前", "後退", "貼耳"],
    "鼓組/節奏 (Drums)": ["鼓", "大鼓", "小鼓", "hihat", "鈸", "節奏", "punch", "重音", "力道", "敲擊", "太響", "太炸"],
    "低頻/貝斯 (Bass & Sub)": ["低音", "bass", "貝斯", "下潛", "低頻", "轟", "糊", "濁", "髒", "肥"],
    "吉他/樂器 (Instruments)": ["吉他", "鋼琴", "弦樂", "合成器", "鍵盤", "伴奏", "solo", "鋪底", "墊樂"],
    "空間/殘響 (Space & Reverb)": ["殘響", "reverb", "空間", "回音", "delay", "延遲", "太濕", "太乾", "空靈", "立體", "廣度", "寬度"],
    "動態與平衡 (Balance & Master)": ["整體", "大氣", "壓得太死", "音量", "總音量", "爆了", "破音", "動態", "太大聲", "太小聲"]
}

def rule_based_extract(text: str) -> dict:
    """Fallback parser when no API key is provided."""
    sentences = re.split(r'[，。！？\n；,!?]+', text)
    classified = {category: [] for category in KEYWORDS_MAP}
    uncategorized = []
    
    for s in sentences:
        s = s.strip()
        if not s or len(s) < 2:
            continue
        matched = False
        for category, words in KEYWORDS_MAP.items():
            if any(w.lower() in s.lower() for w in words):
                classified[category].append(s)
                matched = True
        if not matched:
            uncategorized.append(s)
            
    return {
        "classified": {k: v for k, v in classified.items() if v},
        "uncategorized": uncategorized
    }

def analyze_with_ai_or_rules(text: str, api_key: str = None) -> tuple:
    """Analyze using Gemini AI if key provided, else fallback to rule-based parser."""
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            prompt = f"""你是一名頂級商業混音師與音樂製作人助理。請將以下客戶在微信語音轉出來的雜亂口語意見，轉化為兩份專業文案：

客戶原始文字：
\"\"\"{text}\"\"\"

請嚴格以 JSON 格式輸出，結構如下：
{{
  "internal_tasks": [
    {{"track": "人聲/鼓組/低頻/吉他/空間/整體", "issue": "客戶聽到的問題", "action": "具體混音操作建議（如EQ/壓限/推桿/殘響調整）"}}
  ],
  "client_summary": [
    "用禮貌、專業且精確的語氣列出的修改項目（例如：1. 【人聲】提升清晰度與微調音量平衡）"
  ],
  "risk_warning": "若客戶提出推翻架構或換素材的要求，提出預警；若無則留空"
}}
請僅輸出純 JSON，不要加額外解釋。
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            raw_json = response.text.strip()
            # Clean markdown codeblocks if present
            raw_json = re.sub(r'^```json\s*', '', raw_json)
            raw_json = re.sub(r'```$', '', raw_json).strip()
            data = json.loads(raw_json)
            
            # Format internal markdown
            internal_md = ["### 🎛️ AI 混音工程執行清單 (Action Items)\n"]
            for idx, task in enumerate(data.get("internal_tasks", []), 1):
                internal_md.append(f"- [ ] **[項目 {idx}] 【{task.get('track')}】**")
                internal_md.append(f"  - 👂 客戶反饋：{task.get('issue')}")
                internal_md.append(f"  - 🔧 混音建議：{task.get('action')}\n")
                
            if data.get("risk_warning"):
                internal_md.append(f"> ⚠️ **製作人風險提醒**：{data.get('risk_warning')}\n")
                
            # Format client summary
            client_items = "\n".join([f"{idx}. {item}" for idx, item in enumerate(data.get("client_summary", []), 1)])
            
            return "\n".join(internal_md), client_items, True
        except Exception as e:
            st.sidebar.error(f"AI 調用出錯，自動退回規則解析：{str(e)}")
            
    # Fallback to rules
    parsed = rule_based_extract(text)
    internal_md = format_internal_items(parsed, text)
    client_items = []
    idx = 1
    for cat, items in parsed.get("classified", {}).items():
        short_cat = cat.split(" ")[0]
        for it in items:
            client_items.append(f"{idx}. 【{short_cat}】{it}")
            idx += 1
    if not client_items and parsed.get("uncategorized"):
        for it in parsed["uncategorized"]:
            client_items.append(f"{idx}. {it}")
            idx += 1
    return internal_md, "\n".join(client_items), False


def format_client_reply(song_name: str, version: str, classified_data: dict) -> str:
    """Format professional reply for WeChat client."""
    items_summary = []
    idx = 1
    for cat, items in classified_data.get("classified", {}).items():
        short_cat = cat.split(" ")[0]
        for it in items:
            items_summary.append(f"{idx}. 【{short_cat}】{it}")
            idx += 1
            
    if not items_summary and classified_data.get("uncategorized"):
        for it in classified_data["uncategorized"]:
            items_summary.append(f"{idx}. {it}")
            idx += 1

    summary_text = "\n".join(items_summary) if items_summary else "1. 細部音色平衡與空間感優化"
    
    reply = f"""老師/老闆您好！已收到《{song_name}》的修改想法，智翔與團隊已幫您梳理出本次【{version}】具體修改清單：

{summary_text}

📌 為確保修改方向精確到位，我們將依上述清單逐一精調。若確認無誤，工程師立刻啟動調整並於完成後第一時間回傳給您試聽！謝謝您！"""
    return reply

# Sidebar: Project & Scope Config
with st.sidebar:
    st.title("🎛️ 專案設定與防禦守衛")
    st.caption("林从胤音樂工作室 · AI 混音修改意見管理")
    
    song_name = st.text_input("歌曲名稱 / 案名", value="專案歌曲")
    client_name = st.text_input("客戶稱呼 / 來源", value="外部客戶")
    
    version_options = ["v1 (初版微調)", "v2 (第 2 次修改)", "v3 (第 3 次修改 - 免費上限)", "v4 (第 4 次 - 進入計費階段)", "v5+ (極限止損版)"]
    selected_version = st.selectbox("當前修改版本進度", version_options, index=1)
    
    # Financial / Scope Guard Badge
    if "v1" in selected_version or "v2" in selected_version:
        st.success("🟢 正常修改範圍（包含在合約/預設次數內）")
    elif "v3" in selected_version:
        st.warning("🟡 注意：已達第 3 次修改上限！本次後若再改需另計費用。")
    else:
        st.error("🔴 警戒：已超過 3 次！依約進入 500~1000 計費階段，請勿無限制增加新需求。")

    st.markdown("---")
    st.subheader("🤖 AI 增強設定 (可選)")
    api_key = st.text_input("Gemini API Key (選填)", type="password", help="若填入 API Key 可開啟智慧總結與音樂行話專業重構；不填則使用內建音樂關鍵字語意解析。")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        st.caption("✨ 已啟用 Gemini AI 深度提煉模式")
    else:
        st.caption("⚡ 運行於本機極速語意規則模式 (零延遲、免 Key)")

# Main Interface
st.title("🎛️ AI 混音修改意見智能提煉工廠")
st.markdown("將客戶在微信語音轉出來的**零散口語、情緒形容詞**，一秒提煉成**專業混音清單**與**標準客戶回覆**。")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 1. 貼入微信語音轉文字內容")
    sample_text = "阿葆智翔啊，那個前奏吉他好像有點太亮了，聽起來有點刺耳。副歌那邊主唱聲音有點被鼓吃掉，能不能把人聲推前面一點？然後最後面的殘響有點太濕了，聽起來濁濁的，整體低音再扎實一點點就好。"
    
    user_input = st.text_area(
        "直接在微信對話框長按語音「轉文字」後，複製貼在這裡：",
        height=220,
        placeholder="例如：那個副歌人聲太小了啦，然後大鼓聽起來不夠重，結尾回音太長..."
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        load_sample = st.button("帶入範例文字測試")
    with col_btn2:
        clear_input = st.button("清空輸入")

    if load_sample:
        user_input = sample_text

    st.markdown("---")
    st.info("💡 **小撇步**：客戶通常習慣一小句一小句發語音，你可以把微信上轉出來的多段文字一口氣全選複製、貼在上面，系統會自動融合成一張完整工單！")

with col2:
    st.subheader("📤 2. 智能提煉成果")
    
    if user_input.strip():
        # Parsing with AI or Rules
        internal_todo, client_items_text, is_ai = analyze_with_ai_or_rules(user_input, api_key)
        
        # Format client message
        version_tag = selected_version.split(" ")[0]
        client_msg = f"""老師/老闆您好！已收到《{song_name}》的修改想法，智翔與團隊已幫您梳理出本次【{version_tag}】具體修改清單：

{client_items_text}

📌 為確保修改方向精確到位，我們將依上述清單逐一精調。若確認無誤，工程師立刻啟動調整並於完成後第一時間回傳給您試聽！謝謝您！"""

        tab1, tab2, tab3 = st.tabs(["📋 混音師執行清單 (內部用)", "💬 客戶確認回覆 (貼微信)", "🔍 原始關鍵字分析"])
        
        with tab1:
            st.markdown(internal_todo)
            st.code(internal_todo, language="markdown")
            
        with tab2:
            st.markdown("##### 📌 直接全選複製貼回微信給客戶：")
            st.text_area("回覆文案預覽", value=client_msg, height=220)
            st.caption("🛡️ 此話術已自動植入邊界定錨，防止客戶改完又反悔！")
            
        with tab3:
            parsed_debug = rule_based_extract(user_input)
            st.write("識別到的關鍵軌道分佈：")
            st.json(parsed_debug["classified"])
            if parsed_debug["uncategorized"]:
                st.write("未能精確分類的句子：")
                st.write(parsed_debug["uncategorized"])
    else:
        st.write("👈 請在左側貼入文字，提煉成果會即時顯示在此。")

st.markdown("---")
st.caption("林从胤音樂專案 · 智能混音管線升級工具組 · Antigravity Automated Audio Operations")
