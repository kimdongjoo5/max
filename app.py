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
# 🎨 초압축 & 게임 UI 스타일 (CSS 마법)
# ==========================================
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .main-title { color: #2c3e50; font-size: 1.8rem; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    
    /* 핵심 마법: 스트림릿 버튼들을 세로가 아닌 '가로'로 텍스트처럼 나열되게 만듦 */
    div.stButton {
        display: inline-block !important;
        width: auto !important;
        margin: 2px !important;
    }
    div.stButton > button {
        padding: 4px 10px !important;
        border-radius: 12px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
        min-height: 26px !important;
        height: auto !important;
        line-height: 1.2 !important;
        border: 1px solid #dcdde1 !important;
        background-color: #f1f2f6;
        color: #2f3640;
    }
    /* 빈자리(참여) 버튼 스타일 */
    div.stButton > button[kind="primary"] {
        background-color: #e8f4fd !important;
        border: 1px dashed #3498db !important;
        color: #3498db !important;
    }
    /* 버튼에 마우스 올렸을 때 (내 자리 뺄 때 직관적으로 보이게) */
    div.stButton > button:hover:not([disabled]) {
        border-color: #e74c3c !important;
        color: #e74c3c !important;
    }
    /* 남의 이름이나 꽉 찬 자리는 희미하게 */
    div.stButton > button[disabled] {
        opacity: 0.7 !important;
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
# 🔗 상단 퀵 링크 (모바일 가로 배열 알약 버튼)
# ==========================================
links = [
    {"n": "거래소", "url": "https://www.classicbaram.gg/trade", "i": "💰"},
    {"n": "체마계산", "url": "https://www.classicbaram.gg/calc/kingQuest/recommend", "i": "🧮"},
    {"n": "갤러리", "url": "https://enter.dcinside.com/mgallery/board/lists/?id=wcserver", "i": "💬"},
    {"n": "의상실", "url": "https://barambook.com/render", "i": "👗"},
    {"n": "패치노트", "url": "https://www.classicbaram.gg/patchNotes", "i": "📜"}
]

# HTML/CSS Flexbox로 모바일에서도 절대 안 깨지고 가로로 모이게 만듦
links_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 20px;">'
for l in links:
    links_html += f'<a href="{l["url"]}" target="_blank" style="background: white; border: 1px solid #ddd; border-radius: 20px; padding: 6px 14px; font-size: 0.8rem; font-weight: bold; color: #2c3e50; text-decoration: none; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">{l["i"]} {l["n"]}</a>'
links_html += '</div>'
st.markdown(links_html, unsafe_allow_html=True)


# ==========================================
# 👤 로그인 및 날짜 설정
# ==========================================
st.error("🚨 [필수] 아래에 닉네임을 입력해야 '빈자리' 버튼을 누를 수 있습니다!")
col_l, col_d = st.columns([2, 1])
with col_l: u_name = st.text_input("🛡️ 닉네임 입력 (입력 후 엔터)", placeholder="예: 지존전사")
with col_d: g_date = str(st.date_input("📅 날짜", value=date.today()))

is_logged = False
if u_name:
    if u_name not in users_db:
        job = st.selectbox("직업을 먼저 선택해주세요", JOB_LIST)
        if st.button("내 직업 저장하기"):
