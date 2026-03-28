import streamlit as st
import json
import os
import uuid
from datetime import date
from streamlit_autorefresh import st_autorefresh

# 10초마다 자동 갱신
st_autorefresh(interval=10000, key="datarefresh")

USER_DB_FILE = "users_db.json"
PARTY_DB_FILE = "parties_db.json"
CATEGORIES = ["일일숙제(600)", "일일숙제(청명파티)", "사냥파티", "퀘스트(용궁 등)", "어금니", "해골왕", "폭염왕"]
JOB_LIST = ["전사", "도적", "주술사", "도사"]

st.set_page_config(page_title="천국문파 예약 시스템", layout="wide")

# ==========================================
# 🎨 UI 스타일 (알록달록 배지버튼 & 글씨 축소)
# ==========================================
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .main-title { color: #2c3e50; font-size: 1.6rem; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    
    /* 카드 컨테이너 내부 여백 줄이기 */
    [data-testid="stVerticalBlockBorderWrapper"] { padding: 0.4rem !important; }

    /* 버튼을 이름표(배지) 모양으로 완벽 위장 */
    div.stButton { display: inline-block !important; width: auto !important; margin: 2px !important; }
    div.stButton > button {
        padding: 2px 6px !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
        min-height: 24px !important;
        line-height: 1.2 !important;
    }
    
    /* 1. 남의 이름 (파란색 배지 - 클릭 불가) */
    div.stButton > button[disabled] {
        background-color: #3498db !important;
        color: white !important;
        border: none !important;
        opacity: 1 !important;
    }
    
    /* 2. 내 이름 / 나가기 (빨간색 배지) */
    div.stButton > button:not([disabled]):not([kind="primary"]) {
        background-color: #e74c3c !important;
        color: white !important;
        border: none !important;
    }
    div.stButton > button:not([disabled]):not([kind="primary"]):hover {
        background-color: #c0392b !important;
    }
    
    /* 3. 빈자리 / 참여 (회색 점선 배지) */
    div.stButton > button[kind="primary"] {
        background-color: #f1f2f6 !important;
        color: #7f8c8d !important;
        border: 1px dashed #bdc3c7 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        border-color: #3498db !important;
        color: #3498db !important;
        background-color: #e8f4fd !important;
    }
</style>
""", unsafe_allow_html=True)

def load_json(f_path, default):
    if os.path.exists(f_path):
        with open(f_path, "r", encoding="utf-8") as f: return json.load(f)
    return default

def save_json(f_path, data):
    with open(f_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

users_db = load_json(USER_DB_FILE, {})
parties_db = load_json(PARTY_DB_FILE, {})

st.markdown('<div class="main-title">⚔️ 천국문파 파티 예약 시스템</div>', unsafe_allow_html=True)

# ==========================================
# 🔗 상단 퀵 링크 (알약 버튼)
# ==========================================
links = [
    {"n": "거래소", "url": "https://www.classicbaram.gg/trade", "i": "💰"},
    {"n": "체마계산", "url": "https://www.classicbaram.gg/calc/kingQuest/recommend", "i": "🧮"},
    {"n": "갤러리", "url": "https://enter.dcinside.com/mgallery/board/lists/?id=wcserver", "i": "💬"},
    {"n": "의상실", "url": "https://barambook.com/render", "i": "👗"},
    {"n": "패치노트", "url": "https://www.classicbaram.gg/patchNotes", "i": "📜"}
]

links_html = '<div style="display: flex; flex-wrap: wrap
