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
CATEGORIES = ["일일숙제(600)", "일일숙제(청명파티)", "사냥파티", "4차팟", "3차팟", "퀘스트(용궁 등)", "어금니", "해골왕", "폭염왕"]
JOB_LIST = ["전사", "도적", "주술사", "도사"]

st.set_page_config(page_title="천국문파 예약 시스템", layout="wide")

# ==========================================
# 🎨 UI 스타일 (강제 2열 고정 마법 적용!)
# ==========================================
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .main-title { color: #2c3e50; font-size: 1.6rem; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    
    [data-testid="stVerticalBlockBorderWrapper"] { padding: 0.4rem !important; }

    /* 🔥 핵심 마법: 파티 카드 내부의 참가자 슬롯을 모바일/PC 상관없이 무조건 2열로 강제 고정 */
    div[data-testid="stVerticalBlockBorderWrapper"] div.stButton {
        display: inline-block !important;
        width: calc(50% - 6px) !important; /* 정확히 절반 너비 차지 */
        margin: 3px !important;
        vertical-align: top !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] div.stButton > button {
        width: 100% !important; /* 버튼이 허여멀건하게 비지 않고 꽉 차게 */
        padding: 4px 0px !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
        min-height: 24px !important;
        line-height: 1.2 !important;
    }
    
    div.stButton > button[disabled] { background-color: #3498db !important; color: white !important; border: none !important; opacity: 1 !important; }
    div.stButton > button:not([disabled]):not([kind="primary"]) { background-color: #e74c3c !important; color: white !important; border: none !important; }
    div.stButton > button:not([disabled]):not([kind="primary"]):hover { background-color: #c0392b !important; }
    div.stButton > button[kind="primary"] { background-color: #f1f2f6 !important; color: #7f8c8d !important; border: 1px dashed #bdc3c7 !important; }
    div.stButton > button[kind="primary"]:hover { border-color: #3498db !important; color: #3498db !important; background-color: #e8f4fd !important; }
    
    div.row-widget.stRadio > div { flex-wrap: wrap; gap: 5px; }
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

def classify_time(time_str):
    if "심야" in time_str: return "night"
    try:
        am_pm, hr_str = time_str.split("~")[0].strip().split(" ")
        hr = int(hr_str.replace("시", ""))
        if am_pm == "오후" and hr != 12: hr += 12
        elif am_pm == "오전" and hr == 12: hr = 0
        if 0 <= hr < 6: return "night"
        elif 6 <= hr < 12: return "am"
        else: return "pm"
    except: return "pm"

# ==========================================
# 🧹 과거 데이터 자동 삭제 (24시간 폭파)
# ==========================================
today_str = str(date.today())
cleaned = False
for cat in list(parties_db.keys()):
    for d in list(parties_db[cat].keys()):
        if d < today_str:
            del parties_db[cat][d]
            cleaned = True
if cleaned: save_json(PARTY_DB_FILE, parties_db)

st.markdown('<div class="main-title">⚔️ 천국문파 파티 예약 시스템</div>', unsafe_allow_html=True)

# ==========================================
# 🔗 상단 퀵 링크 (3행 2열 바둑판)
# ==========================================
links = [
    {"n": "거래소", "url": "https://www.classicbaram.gg/trade", "i": "💰"},
    {"n": "체마계산", "url": "https://www.classicbaram.gg/calc/kingQuest/recommend", "i": "🧮"},
    {"n": "갤러리", "url": "https://enter.dcinside.com/mgallery/board/lists/?id=wcserver", "i": "💬"},
    {"n": "의상실", "url": "https://barambook.com/render", "i": "👗"},
    {"n": "패치노트", "url": "https://www.classicbaram.gg/patchNotes", "i": "📜"}
]

links_html = '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 20px;">'
for l in links:
    links_html += f'<a href="{l["url"]}" target="_blank" style="background: white; border: 1px solid #ddd; border-radius: 12px; padding: 8px; font-size: 0.8rem; font-weight: bold; color: #2c3e50; text-decoration: none; box-shadow: 0 1px 2px rgba(0,0,0,0.05); text-align: center;">{l["i"]} {l["n"]}</a>'
links_html += '</div>'
st.markdown(links_html, unsafe_allow_html=True)

# ==========================================
# 👤 로그인 및 날짜 설정
# ==========================================
col_l, col_d = st.columns([2, 1])
with col_l: u_name = st.text_input("🛡️ 닉네임 (입력해야 참여 가능)", placeholder="예: 지존전사")
with col_d: g_date = str(st.date_input("📅 날짜", value=date.today()))

is_logged = False
if u_name:
    if u_name not in users_db:
        job = st.selectbox("직업을 먼저 선택해주세요", JOB_LIST)
        if st.button("내 직업 저장하기"):
            users_db[u_name] = job; save_json(USER_DB_FILE, users_db); st.rerun()
    else: is_logged = True

st.write("---")
t_home, t_manage = st.tabs(["🏠 실시간 현황", "➕ 파티 만들기"])

# ==========================================
# 🃏 카드 렌더링 함수 (파이썬 열 나누기 제거, CSS에 맡김)
# ==========================================
def render_party_card(p, d_list):
    p_id, cap, mems = p["id"], p["capacity"], p["members"]
    with st.container(border=True):
        st.markdown(f'<div style="font-weight:900; font-size:0.85rem; display:flex; justify-content:space-between; margin-bottom:2px;"><span>⏰ {p["time"]}</span><span style="color:#e74c3c">{len(mems)}/{cap}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.7rem; color:#7f8c8d; margin-bottom:8px;">🎯 {", ".join(p.get("req_jobs", [])) or "직업 무관"}</div>', unsafe_allow_html=True)

        slots = [{"t": "m", "v": m}
