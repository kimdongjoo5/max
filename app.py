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

# 모바일 호환 및 아이콘/버튼 초압축 디자인 CSS
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    .main-title { color: #2c3e50; font-size: 2rem; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    
    /* 퀵 링크 카드 (기본 사이즈) */
    .link-box { text-align: center; padding: 6px; background: #fdfdfd; border-radius: 8px; border: 1px solid #eee; text-decoration: none; color: black; display: block; }
    .link-icon { font-size: 1.2rem; margin-bottom: 2px; }
    .link-text { font-size: 0.75rem; font-weight: bold; }
    
    /* 파티 카드 */
    .party-card { background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #ddd; margin-bottom: 5px; }
    .p-head { display: flex; justify-content: space-between; font-weight: 900; font-size: 0.95rem; border-bottom: 1px dashed #eee; padding-bottom: 4px; margin-bottom: 6px; }
    .p-job { font-size: 0.75rem; color: #777; margin-bottom: 6px; }
    .m-badge { background: #3498db; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin: 1px; display: inline-block; }
    .m-badge.me { background: #e74c3c; border: 1px solid #c0392b; }
    .e-slot { background: #f1f2f6; color: #a4b0be; border: 1px dashed #ccc; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin: 1px; display: inline-block; }
    
    /* 버튼 얇고 작게 깎기 */
    div.stButton { margin-top: 5px !important; }
    div.stButton > button {
        padding: 2px 12px !important;
        font-size: 0.8rem !important;
        min-height: 28px !important;
        border-radius: 6px !important;
        width: auto !important; 
        display: inline-block !important;
    }

    /* 모바일 환경(화면이 좁을 때) 초소형 압축! */
    @media (max-width: 768px) {
        .main-title { font-size: 1.4rem !important; }
        .link-icon { font-size: 0.9rem !important; }      
        .link-text { font-size: 0.55rem !important; }     
        .link-box { padding: 2px !important; }            
        .m-badge, .e-slot { font-size: 0.7rem !important; }
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

# --- 퀵 링크 (5개) ---
links = [
    {"n": "거래소", "url": "https://www.classicbaram.gg/trade", "i": "💰"},
    {"n": "체마계산", "url": "https://www.classicbaram.gg/calc/kingQuest/recommend", "i": "🧮"},
    {"n": "클바갤러리", "url": "https://enter.dcinside.com/mgallery/board/lists/?id=wcserver", "i": "💬"},
    {"n": "의상실", "url": "https://barambook.com/render", "i": "👗"},
    {"n": "패치노트", "url": "https://www.classicbaram.gg/patchNotes", "i": "📜"}
]
cols = st.columns(5)
for i, l in enumerate(links):
    with cols[i]:
        st.markdown(f'<a href="{l["url"]}" target="_blank" class="link-box"><div class="link-icon">{l["i"]}</div><div class="link-text">{l["n"]}</div></a>', unsafe_allow_html=True)

st.write("")

# --- 로그인 및 날짜 ---
st.error("🚨 [필수 확인] 아래에 닉네임을 입력해야만 파티 예약 및 취소가 가능합니다!")
col_l, col_d = st.columns([2, 1])
with col_l: u_name = st.text_input("🛡️ 닉네임 입력 (입력 후 엔터)", placeholder="예: 지존전사")
with col_d: g_date = str(st.date_input("📅 날짜", value=date.today()))

is_logged = False
if u_name:
    if u_name not in users_db:
        job = st.selectbox("직업을 먼저 선택해주세요", JOB_LIST)
        if st.button("내 직업 저장하기"):
            users_db[u_name] = job; save_json(USER_DB_FILE, users_db); st.rerun()
    else:
        is_logged = True

st.write("---")

t_home, t_manage = st.tabs(["🏠 실시간 현황", "➕ 파티 만들기"])

# --- 홈 (실시간 현황) ---
with t_home:
    any_p = False
    for cat in CATEGORIES:
        d_list = parties_db.get(cat, {}).get(g_date, [])
        if d_list:
            any_p = True
            st.markdown(f"#### 📌 {cat}")
            p_cols = st.columns(3)
            for idx, p in enumerate(d_list):
                with p_cols[idx % 3]:
                    p_id, cap, mems = p["id"], p["capacity"], p["members"]
                    
                    html = f'<div class="party-card"><div class="p-head"><span>⏰ {p["time"]}</span><span style="color:#e74c3c">{len(mems)}/{cap}</span></div><div class="p-job">🎯 {", ".join(p.get("req_jobs", [])) or "직업 무관"}</div><div>'
                    for m in mems:
                        html += f'<span class="m-badge {"me" if m==u_name else ""}">[{users_db.get(m, "?")}] {m}</span>'
                    for _ in range(cap - len(mems)):
                        html += '<span class="e-slot">빈자리</span>'
                    html += '</div></div>'
                    st.markdown(html, unsafe_allow_html=True)
                    
                    if is_logged:
                        if u_name in mems:
                            if st.button("❌ 내 자리 빼기", key=f"
